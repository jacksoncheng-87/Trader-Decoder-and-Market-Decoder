# src/trade_decoder.py
import json
import os
import argparse
from decimal import Decimal
from web3 import Web3
from dotenv import load_dotenv
from src.constants import EXCHANGE_ADDRESSES, ORDER_FILLED_ABI

# 加载环境变量
load_dotenv()

def decode_trade(tx_hash: str):
    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        raise ValueError("请在 .env 文件中配置 RPC_URL")
    
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # 1. 获取交易回执
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
    except Exception as e:
        print(f"获取交易失败: {e}")
        return []

    # 创建合约对象用于解码事件
    contract = w3.eth.contract(abi=[ORDER_FILLED_ABI])
    
    decoded_trades = []

    # 2. 遍历日志寻找 OrderFilled 事件
    for log in receipt['logs']:
        # 检查是否来自 Polymarket 交易所合约
        if log['address'] not in EXCHANGE_ADDRESSES:
            continue
            
        try:
            # 解析日志
            parsed_log = contract.events.OrderFilled().process_log(log)
            args = parsed_log['args']
            
            # =========== 【新增修复】 过滤掉 Taker 为交易所的汇总日志 ===========
            # 如果 taker 是交易所地址本身，说明这是汇总记录，跳过，防止双重计数
            if args['taker'] in EXCHANGE_ADDRESSES:
                continue
            # ================================================================
            
            # 3. 解析字段含义
            maker_asset_id = args['makerAssetId']
            taker_asset_id = args['takerAssetId']
            maker_amount = args['makerAmountFilled']
            taker_amount = args['takerAmountFilled']
            
            # 4. 判断买卖方向和计算价格
            # 资产 ID 为 0 代表 USDC
            price = Decimal(0)
            token_id = ""
            side = ""
            
            # 精度处理：USDC 和 Token 通常都需除以 1e6
            maker_amt_dec = Decimal(maker_amount) / Decimal(10**6)
            taker_amt_dec = Decimal(taker_amount) / Decimal(10**6)

            if maker_asset_id == 0: 
                # Maker 支付 USDC (ID=0), 获得 Token
                # 动作: Maker BUY
                side = "BUY"
                token_id = hex(taker_asset_id)
                # 价格 = 支付的 USDC / 获得的 Token
                price = maker_amt_dec / taker_amt_dec if taker_amt_dec > 0 else 0
                
            else:
                # Maker 支付 Token, 获得 USDC (TakerAssetId=0)
                # 动作: Maker SELL (因为 Taker 支付 USDC)
                side = "SELL"
                token_id = hex(maker_asset_id)
                # 价格 = 获得的 USDC / 支付的 Token
                price = taker_amt_dec / maker_amt_dec if maker_amt_dec > 0 else 0

            trade_info = {
                "txHash": tx_hash,
                "logIndex": log['logIndex'],
                "exchange": log['address'],
                "maker": args['maker'],
                "taker": args['taker'],
                "makerAssetId": str(maker_asset_id),
                "takerAssetId": str(taker_asset_id),
                "makerAmountFilled": str(maker_amount),
                "takerAmountFilled": str(taker_amount),
                "price": f"{price:.4f}", # 保留4位小数
                "tokenId": token_id,
                "side": side
            }
            decoded_trades.append(trade_info)
            
        except Exception as e:
            # 可能是非 OrderFilled 事件，跳过
            continue

    return decoded_trades

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Polymarket Trade Decoder")
    parser.add_argument("--tx-hash", required=True, help="Transaction Hash")
    parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    trades = decode_trade(args.tx_hash)
    json_output = json.dumps(trades, indent=2)
    
    print(json_output)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(json_output)