# Trader-Decoder-and-Market-Decoder
trade_decoder 能正确解析 OrderFilled 事件并输出交易详情  trade_decoder 正确计算 price、side、token_id  trade_decoder 正确过滤 taker == exchange 的重复日志 ，market_decoder 能从 Gamma API 获取市场信息 ，market_decoder 能正确计算 yesTokenId 和 noTokenId ，计算得到的 TokenId 与 Gamma API 返回的 clobTokenIds 一致 、demo 脚本能整合两个任务并输出完整结果
