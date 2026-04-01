from alphabet import AlphabetOps
from caesar import CaesarCipher

# S-блоки (lab1)
class SBlock:
    @staticmethod
    def _compute_permutation(key: str) -> list:
        arr = AlphabetOps.text2array(key)
        s = 0
        for i in range(16):
            sign = 1 if i % 2 == 0 else -1
            s = (48 + s + sign * arr[i]) % 24
        M = [0, 1, 2, 3]
        for k in range(3):
            t = s % (4 - k)
            s = (s - t) // (4 - k)
            M[k], M[k + t] = M[k + t], M[k]
        return M

    @staticmethod
    def frw_S_Caesar(block: str, key: str) -> str:
        if len(block) != 4 or len(key) != 16:
            return "input_error"
        key_tmp = CaesarCipher._build_key_tmp(key)
        return CaesarCipher.frw_poly_Caesar(block, key_tmp)

    @staticmethod
    def inv_S_Caesar(block: str, key: str) -> str:
        if len(block) != 4 or len(key) != 16:
            return "input_error"
        key_tmp = CaesarCipher._build_key_tmp(key)
        return CaesarCipher.inv_poly_Caesar(block, key_tmp)

    @staticmethod
    def frw_merge_block(block: str, key: str) -> str:
        if len(block) != 4 or len(key) != 16:
            return "input_error"
        M = SBlock._compute_permutation(key)
        inp = AlphabetOps.text2array(block)
        for j in range(4):
            b, a = M[(j + 1) % 4], M[j % 4]
            inp[b] = (inp[b] + inp[a]) % 32
        return AlphabetOps.array2text(inp)

    @staticmethod
    def inv_merge_block(block: str, key: str) -> str:
        if len(block) != 4 or len(key) != 16:
            return "input_error"
        M = SBlock._compute_permutation(key)
        inp = AlphabetOps.text2array(block)
        for j in range(3, -1, -1):
            b, a = M[(j + 1) % 4], M[j % 4]
            inp[b] = (inp[b] - inp[a] + 32) % 32
        return AlphabetOps.array2text(inp)

    @staticmethod
    def frw_S_CaesarM(block: str, key: str) -> str:
        tmp = SBlock.frw_merge_block(block, key)
        tmp = SBlock.frw_S_Caesar(tmp, key)
        return SBlock.frw_merge_block(tmp, key)

    @staticmethod
    def inv_S_CaesarM(block: str, key: str) -> str:
        tmp = SBlock.inv_merge_block(block, key)
        tmp = SBlock.inv_S_Caesar(tmp, key)
        return SBlock.inv_merge_block(tmp, key)
