import json
import redis
from typing import Optional, Dict, Any, List
from config.settings import settings
from datetime import datetime, timedelta

class RedisService:
    def __init__(self):
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.available = True
            self.redis.ping()
        except:
            self.available = False
            self.redis = None
    
    def is_available(self) -> bool:
        if not self.available:
            return False
        try:
            self.redis.ping()
            return True
        except:
            self.available = False
            return False
    
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        if not self.is_available():
            return
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        if expire:
            self.redis.setex(key, expire, value)
        else:
            self.redis.set(key, value)
    
    def get(self, key: str) -> Optional[Any]:
        if not self.is_available():
            return None
        
        value = self.redis.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except:
            return value
    
    def delete(self, key: str):
        if not self.is_available():
            return
        self.redis.delete(key)
    
    def increment(self, key: str, amount: int = 1) -> int:
        if not self.is_available():
            return 0
        return self.redis.incrby(key, amount)
    
    def expire(self, key: str, seconds: int):
        if not self.is_available():
            return
        self.redis.expire(key, seconds)
    
    def hset(self, name: str, key: str, value: Any):
        if not self.is_available():
            return
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.redis.hset(name, key, value)
    
    def hget(self, name: str, key: str) -> Optional[Any]:
        if not self.is_available():
            return None
        value = self.redis.hget(name, key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except:
            return value
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        if not self.is_available():
            return {}
        data = self.redis.hgetall(name)
        result = {}
        for k, v in data.items():
            try:
                result[k] = json.loads(v)
            except:
                result[k] = v
        return result
    
    def hincrby(self, name: str, key: str, amount: int = 1) -> int:
        if not self.is_available():
            return 0
        return self.redis.hincrby(name, key, amount)
    
    def zadd(self, name: str, mapping: Dict[str, float]):
        if not self.is_available():
            return
        self.redis.zadd(name, mapping)
    
    def zrevrange(self, name: str, start: int = 0, end: int = -1, withscores: bool = False):
        if not self.is_available():
            return []
        return self.redis.zrevrange(name, start, end, withscores=withscores)
    
    def zincrby(self, name: str, amount: float, member: str) -> float:
        if not self.is_available():
            return 0.0
        return self.redis.zincrby(name, amount, member)

redis_service = RedisService()
