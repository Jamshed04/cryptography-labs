from blocks import BlockOps
from core import CoreCrypto
from alphabet import AlphabetOps

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

    @staticmethod
    def KDF(
            MAT_IN: str,
            SALT_IN: str,
            CON_IN: list[str],
            SIZE_IN: list[int],
            iter_in: int,
    ):
        tmp = MAT_IN + SALT_IN

        for _ in range(iter_in + 1):
            ext = HashFunc.MerDam_hash(tmp)
            tmp = ext + tmp

        PRK = tmp
        out = []

        for i in range(len(SIZE_IN)):
            q = (SIZE_IN[i] + 63) // 64

            rem = i
            res = ""

            while rem > 0:
                h = rem % 32
                res += AlphabetOps.num2sym(h)
                rem = (rem - h) // 32

            if q > 0:
                hash_val = PRK
                for _ in range(q):
                    tmp = hash_val + CON_IN[i] + PRK
                    hash_val = HashFunc.MerDam_hash(tmp)
                    res = hash_val + res
            else:
                tmp = PRK + CON_IN[i] + PRK
                res = HashFunc.MerDam_hash(tmp)

            out_i = res[:SIZE_IN[i]]
            out.append(out_i)

        return out