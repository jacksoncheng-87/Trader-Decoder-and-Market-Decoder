# src/constants.py

# Polygon USDC.e 地址
COLLATERAL_TOKEN = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

# 交易所合约地址
# CTF Exchange (二元市场)
CTF_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
# NegRisk CTF Exchange (多结果负风险市场)
NEGRISK_CTF_EXCHANGE = "0xC5d563A36AE78145C45a50134d48A1215220f80a"

EXCHANGE_ADDRESSES = [CTF_EXCHANGE, NEGRISK_CTF_EXCHANGE]

# Polymarket Gamma API URL
GAMMA_API_URL = "https://gamma-api.polymarket.com/events"

# OrderFilled 事件的 ABI (简化版，仅包含解码所需部分)
# 字段: maker, taker, makerAssetId, takerAssetId, makerAmountFilled, takerAmountFilled
ORDER_FILLED_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "orderHash", "type": "bytes32"},
        {"indexed": True, "name": "maker", "type": "address"},
        {"indexed": True, "name": "taker", "type": "address"},
        {"indexed": False, "name": "makerAssetId", "type": "uint256"},
        {"indexed": False, "name": "takerAssetId", "type": "uint256"},
        {"indexed": False, "name": "makerAmountFilled", "type": "uint256"},
        {"indexed": False, "name": "takerAmountFilled", "type": "uint256"},
        {"indexed": False, "name": "fee", "type": "uint256"}
    ],
    "name": "OrderFilled",
    "type": "event"
}