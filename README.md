# Trader-Decoder-and-Market-Decoder
trade_decoder 能正确解析 OrderFilled 事件并输出交易详情  trade_decoder 正确计算 price、side、token_id  trade_decoder 正确过滤 taker == exchange 的重复日志 ，market_decoder 能从 Gamma API 获取市场信息 ，market_decoder 能正确计算 yesTokenId 和 noTokenId ，计算得到的 TokenId 与 Gamma API 返回的 clobTokenIds 一致 、demo 脚本能整合两个任务并输出完整结果。


🚀 快速开始
1. 环境准备
确保本地已安装 Python 3.8+。

Bash
# 克隆仓库 (如果你还没克隆)
git clone <your-repo-url>
cd polymarket_decoder

# 安装依赖
pip install -r requirements.txt
2. 配置环境变量
在项目根目录创建一个 .env 文件，并填入你的 Polygon RPC 节点地址（推荐使用 Alchemy 或 Infura）：

Ini, TOML
RPC_URL=[https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY_HERE](https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY_HERE)
🛠 功能模块
任务 A: 交易解码器 (Trade Decoder)
解析指定交易哈希中的 OrderFilled 事件，还原 Polymarket 的订单撮合详情。

核心逻辑：

监听并过滤 Polymarket Exchange 合约的日志。

自动去重：识别并跳过由交易所合约作为 taker 的汇总日志，防止双重计数。

价格计算：基于 makerAssetId 判断买卖方向（Asset ID 0 为 USDC），自动处理 6 位小数精度。

运行命令：

Bash
python -m src.trade_decoder --tx-hash 0x916cad96dd5c219997638133512fd17fe7c1ce72b830157e4fd5323cf4f19946 --output data/trades.json
输出示例 (data/trades.json)：

JSON
[
  {
    "txHash": "0x916cad...",
    "logIndex": 1263,
    "exchange": "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
    "maker": "0x7bb2...",
    "taker": "0x38E5...",
    "price": "0.7700",
    "tokenId": "0xf0f52d...",
    "side": "BUY"
  }
]
任务 B: 市场解码器 (Market Decoder)
结合 Gamma API 与链上算法，反推市场的 Token ID。

核心逻辑：

从 Gamma API 获取 conditionId。

使用 Gnosis CTF 算法计算 Collection ID：

keccak256(0x0, conditionId, 1) -> YES Collection

keccak256(0x0, conditionId, 2) -> NO Collection

结合抵押品地址（USDC）计算最终的 ERC1155 Token ID。

输出结果包含真实的 UMA Oracle 地址。

运行命令：

Bash
python -m src.market_decoder --market-slug will-there-be-another-us-government-shutdown-by-january-31 --output data/market.json
输出示例 (data/market.json)：

JSON
{
  "conditionId": "0x43ec...",
  "oracle": "0x157Ce2d672854c848c9b79C49a8Cc6cc89176a49",
  "questionId": "0xa583...",
  "collateralToken": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
  "yesTokenId": "0xbeaeab...",
  "noTokenId": "0x20c098...",
  "gamma": { ... }
}
🧪 开发笔记
数据源：本项目使用 Polygon Mainnet RPC 进行链上交互。

类型安全：在 utils.py 中强制对十六进制字符串进行 bytes 转换，解决了 Web3.py 新版本的类型检查报错问题。

跨平台兼容：命令脚本已在 Windows PowerShell 环境下测试通过。
