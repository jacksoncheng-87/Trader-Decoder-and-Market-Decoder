# src/utils.py
from web3 import Web3

def calculate_collection_id(condition_id: str, index_set: int) -> str:
    """
    计算集合 ID
    collectionId = keccak256(parentCollectionId, conditionId, indexSet)
    """
    parent_collection_id = b'\x00' * 32  # parentCollectionId 始终为 0
    
    # 确保 condition_id 是 bytes
    if condition_id.startswith('0x'):
        condition_id_bytes = Web3.to_bytes(hexstr=condition_id)
    else:
        condition_id_bytes = Web3.to_bytes(hexstr='0x' + condition_id)
    
    # index_set 转为 32 字节 (big endian)
    index_set_bytes = index_set.to_bytes(32, 'big')
    
    # 拼接并哈希
    packed = parent_collection_id + condition_id_bytes + index_set_bytes
    return Web3.keccak(packed).hex()

def calculate_position_id(collateral_token: str, collection_id: str) -> str:
    """
    计算头寸 Token ID (ERC1155 TokenId)
    tokenId = keccak256(collateralToken, collectionId)
    """
    # 【关键修改】这里显式将 hex string 转回 bytes，以满足 web3.py 的严格类型检查
    collection_id_bytes = Web3.to_bytes(hexstr=collection_id)
    
    return Web3.solidity_keccak(
        ['address', 'bytes32'],
        [collateral_token, collection_id_bytes]
    ).hex()