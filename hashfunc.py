from blocks import BlockOps
from core import CoreCrypto

# Хеш-функция MerDam (lab2)
class HashFunc:
    EPOCH = "ААААЯЯЯЯААЯЯААЯЯ"

    @staticmethod
    def pad_MD(s: str) -> str:
        rem = 64 - (len(s) % 64)
        return s if rem == 64 else s + "_" * rem

    @staticmethod
    def macro(block: str, state: str) -> list:
        A = BlockOps.add_txt(block[0:16], state[0:16])
        B = BlockOps.add_txt(block[16:32], state[16:32])
        C = BlockOps.add_txt(block[32:48], state[32:48])
        D = BlockOps.add_txt(block[48:64], state[48:64])
        E = state[64:80]
        CON = HashFunc.EPOCH
        for _ in range(12):
            E = BlockOps.add_txt(E, CoreCrypto.C_block([A, B, C, D], "16"))
            tmp = BlockOps.blocks_mix(C, D)
            CON = BlockOps.add_txt(CON, HashFunc.EPOCH)
            C, D = tmp[0], tmp[1]
            B = BlockOps.block_mask(B, CON)
            A, B, C, D, E = B, C, D, E, A
        return [A, B, C, D, E]

    @staticmethod
    def MerDam_hash(msg: str) -> str:
        data = HashFunc.pad_MD(msg)
        A = B = C = D = E = "_" * 16
        for i in range(len(data) // 64):
            A, B, C, D, E = HashFunc.macro(data[i * 64:(i + 1) * 64], A + B + C + D + E)
        return (
                CoreCrypto.C_block([A, E], "16") +
                CoreCrypto.C_block([B, E], "16") +
                CoreCrypto.C_block([C, E], "16") +
                CoreCrypto.C_block([D, E], "16")
        )
