from alphabet import AlphabetOps
from blocks import BlockOps

# Шифры Цезаря (lab1)
class CaesarCipher:
    C_ARRAY = [1, -1, 1, 2, -2, 1, 1, 3, -1, 2]

    @staticmethod
    def frw_Caesar(text: str, key: str) -> str:
        key_sym = key[0]
        return "".join(AlphabetOps.add_s(ch, key_sym) for ch in text)

    @staticmethod
    def inv_Caesar(text: str, key: str) -> str:
        key_sym = key[0]
        return "".join(AlphabetOps.sub_s(ch, key_sym) for ch in text)

    @staticmethod
    def frw_poly_Caesar(text: str, key: str) -> str:
        t_k = "_"
        K = len(key)
        result = ""
        for i, ch in enumerate(text):
            t_k = AlphabetOps.add_s(t_k, key[i % K])
            result += AlphabetOps.add_s(ch, t_k)
        return result

    @staticmethod
    def inv_poly_Caesar(text: str, key: str) -> str:
        t_k = "_"
        K = len(key)
        result = ""
        for i, ch in enumerate(text):
            t_k = AlphabetOps.add_s(t_k, key[i % K])
            result += AlphabetOps.sub_s(ch, t_k)
        return result

    @staticmethod
    def _build_key_tmp(key: str) -> str:
        key_tmp = "____"
        key_ext = key + key
        for i in range(8):
            s_tmp = key_ext[i * 2: i * 2 + 4]
            b_tmp = AlphabetOps.text2array(s_tmp)
            a_tmp = [
                (64 + k + CaesarCipher.C_ARRAY[(2 * i + k) % 10] * b_tmp[k]) % 32
                for k in range(4)
            ]
            key_tmp = BlockOps.add_txt(key_tmp, AlphabetOps.array2text(a_tmp))
        return key_tmp