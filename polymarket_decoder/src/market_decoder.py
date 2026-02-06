# src/market_decoder.py
import json
import argparse
import requests
from src.constants import COLLATERAL_TOKEN, GAMMA_API_URL
from src.utils import calculate_collection_id, calculate_position_id

# Polymarket 使用的 UMA Optimistic Oracle V2 (Polygon 真实地址)
UMA_ORACLE_ADDRESS = "0x157Ce2d672854c848c9b79C49a8Cc6cc89176a49"

def fetch_market_info(slug: str):
    """
    从 Gamma API 获取市场信息以获得 conditionId 和 questionId
    """
    params = {"slug": slug}
    try:
        response = requests.get(GAMMA_API_URL, params=params)
        data = response.json()
        
        if not data:
            print("未找到该 Slug 对应的市场")
            return None, None
            
        event = data[0] # 获取第一个匹配的事件
        market = event['markets'][0] # 获取该事件下的第一个市场
        
        # 返回提取的信息 + 原始 Market 数据 (用于填充 gamma 字段)
        info = {
            "conditionId": market['conditionId'],
            "questionId": market['questionID'],
            "oracle": UMA_ORACLE_ADDRESS, 
            "outcomeSlotCount": 2 # 二元市场固定为 2
        }
        return info, market 
    except Exception as e:
        print(f"API 请求失败: {e}")
        return None, None

def decode_market(slug: str = None, condition_id: str = None):
    
    market_data = {}
    gamma_raw_data = {}
    
    # 1. 获取原始参数
    if slug:
        info, raw = fetch_market_info(slug)
        if info:
            market_data.update(info)
            gamma_raw_data = raw # 保存原始数据
    elif condition_id:
        market_data['conditionId'] = condition_id
        market_data['questionId'] = "Unknown (Need Query Log)"
        market_data['oracle'] = UMA_ORACLE_ADDRESS
        market_data['outcomeSlotCount'] = 2
    
    if 'conditionId' not in market_data:
        return {"error": "Missing Condition ID"}

    cid = market_data['conditionId']
    
    # 2. 计算 Collection IDs
    col_id_yes = calculate_collection_id(cid, 1)
    col_id_no = calculate_collection_id(cid, 2)
    
    # 3. 计算 Token IDs (Position IDs)
    yes_token_id = calculate_position_id(COLLATERAL_TOKEN, col_id_yes)
    no_token_id = calculate_position_id(COLLATERAL_TOKEN, col_id_no)
    
    # --- 格式修正：确保以 0x 开头 ---
    if not yes_token_id.startswith("0x"):
        yes_token_id = "0x" + yes_token_id
    if not no_token_id.startswith("0x"):
        no_token_id = "0x" + no_token_id
    
    # 4. 组装最终结果 (完全匹配预期格式)
    result = {
        "conditionId": cid,
        "oracle": market_data.get('oracle'),
        "questionId": market_data.get('questionId'),
        "outcomeSlotCount": market_data.get('outcomeSlotCount'),
        "collateralToken": COLLATERAL_TOKEN,
        "yesTokenId": yes_token_id,
        "noTokenId": no_token_id,
        "gamma": gamma_raw_data # 添加 gamma 字段
    }
    
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Polymarket Market Decoder")
    parser.add_argument("--market-slug", help="Market Slug (e.g. from Polymarket URL)")
    parser.add_argument("--condition-id", help="Condition ID hex string")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    if not args.market_slug and not args.condition_id:
        print("Error: Must provide --market-slug or --condition-id")
        exit(1)
        
    result = decode_market(slug=args.market_slug, condition_id=args.condition_id)
    json_output = json.dumps(result, indent=2)
    
    print(json_output)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(json_output)