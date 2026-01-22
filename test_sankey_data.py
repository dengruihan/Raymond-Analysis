from backend.api.sankey import get_page_flow
import asyncio

async def test():
    result = await get_page_flow(days=7)
    print("返回的数据:")
    print(f"  entry_pages: {result['entry_pages']}")
    print(f"\n  节点数量: {len(result['nodes'])}")
    print("  所有节点:")
    for node in result['nodes']:
        print(f"    - {node['name']}")
    print(f"\n  连线数量: {len(result['links'])}")
    print("  所有连线:")
    for link in result['links']:
        print(f"    {link['source']} -> {link['target']}: {link['value']}")
    
    print("\n\n检查重复节点:")
    node_names = [node['name'] for node in result['nodes']]
    from collections import Counter
    duplicates = {name: count for name, count in Counter(node_names).items() if count > 1}
    if duplicates:
        print(f"  发现重复节点: {duplicates}")
    else:
        print("  没有重复节点")

asyncio.run(test())
