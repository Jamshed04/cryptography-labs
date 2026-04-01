from numeric import NumericOps
from prng import PRNGEngine
from sblock import SBlock
from alphabet import AlphabetOps


# SP-сеть (lab4)
class SPNetwork:
    _LCG_S0 = [[252564, 9109, 961193], [252564, 9109, 961193], [723482, 8677, 983609]]
    _LCG_S1 = [[51190, 7927, 990711], [51190, 7927, 990711], [549234, 6949, 939683]]
    _LCG_S2 = [[227796, 5107, 981875], [227796, 5107, 981875], [167490, 9871, 809137]]
    _LCG_S3 = [[357630, 8971, 948209], [357630, 8971, 948209], [73335, 6779, 1014784]]
    LCG_SET = [_LCG_S0, _LCG_S1, _LCG_S2, _LCG_S3]

    M1 = [[16, 3, 2, 13], [5, 10, 11, 8], [9, 6, 7, 12], [4, 15, 14, 1]]
    M2 = [[7, 14, 4, 9], [12, 1, 15, 6], [13, 8, 10, 3], [2, 11, 5, 16]]
    M3 = [[4, 14, 15, 1], [9, 7, 6, 12], [5, 11, 10, 8], [16, 2, 3, 13]]
    MAGIC_SQUARES = [M1, M2, M3]


    @staticmethod
    def subblocks_xor(blocka_in: str, blockb_in: str) -> str:
        binA = NumericOps.dec2bin(NumericOps.block2num(blocka_in))
        binB = NumericOps.dec2bin(NumericOps.block2num(blockb_in))
        binO = [(binA[i] + binB[i]) % 2 for i in range(20)]
        return NumericOps.num2block(NumericOps.bin2dec(binO))

    @staticmethod
    def block_xor(blocka_in: str, blockb_in: str) -> str:
        if len(blocka_in) != len(blockb_in):
            raise ValueError("block_xor: длины блоков должны совпадать")
        if len(blocka_in) % 4 != 0:
            raise ValueError("block_xor: длина блока должна быть кратна 4")
        nb = len(blocka_in) // 4
        return "".join(
            SPNetwork.subblocks_xor(
                blocka_in[i * 4:(i + 1) * 4],
                blockb_in[i * 4:(i + 1) * 4]
            )
            for i in range(nb)
        )


    @staticmethod
    def produce_round_keys(key_in: str, num_in: int, set_in: list = None) -> list:
        if len(key_in) != 16:
            raise ValueError("produce_round_keys: ключ должен иметь длину 16 символов")
        if num_in <= 0:
            raise ValueError("produce_round_keys: число ключей должно быть > 0")
        if set_in is None:
            set_in = SPNetwork.LCG_SET
        out0, intern = PRNGEngine.C_CT_LSG_NEXT("up", -1, key_in, set_in)
        keys = [out0]
        for _ in range(num_in - 1):
            out_i, intern = PRNGEngine.C_CT_LSG_NEXT("down", intern, -1, set_in)
            keys.append(out_i)
        return keys


    @staticmethod
    def frw_MagicSquare(block_in: str, mat_in: list) -> str:
        if len(block_in) != 16:
            raise ValueError("frw_MagicSquare: блок должен иметь длину 16 символов")
        out = ""
        for i in range(4):
            for j in range(4):
                out += block_in[mat_in[i][j] - 1]
        return out

    @staticmethod
    def inv_MagicSquare(block_in: str, mat_in: list) -> str:
        if len(block_in) != 16:
            raise ValueError("inv_MagicSquare: блок должен иметь длину 16 символов")
        d = AlphabetOps.text2array(block_in)
        tmp = [0] * 16
        for i in range(4):
            for j in range(4):
                tmp[mat_in[i][j] - 1] = d[4 * i + j]
        return AlphabetOps.array2text(tmp)


    @staticmethod
    def LB2B(block_in: str) -> list:
        if len(block_in) != 16:
            raise ValueError("LB2B: блок должен иметь длину 16 символов")
        out = [0] * 80
        for q in range(4):
            tmp = NumericOps.dec2bin(NumericOps.block2num(block_in[q * 4:(q + 1) * 4]))
            out[q * 20:(q + 1) * 20] = tmp
        return out

    @staticmethod
    def B2LB(block_in: list) -> str:
        if len(block_in) != 80:
            raise ValueError("B2LB: длина битового массива должна быть 80")
        out = ""
        for q in range(4):
            out += NumericOps.num2block(NumericOps.bin2dec(block_in[q * 20:(q + 1) * 20]))
        return out

    @staticmethod
    def binary_shift(array_in: list, shift_in: int) -> list:
        s = len(array_in)
        if s == 0:
            return []
        b = shift_in % s
        out = [0] * s
        if b > 0:
            for i in range(b, s):
                out[i] = array_in[i - b]
            for i in range(b):
                out[i] = array_in[s - b + i]
        else:
            for i in range(s + b):
                out[i] = array_in[i - b]
            for i in range(s + b, s):
                out[i] = array_in[i - s - b]
        return out


    @staticmethod
    def frw_P_round(block_in: str, r_in: int) -> str:
        r = r_in % 3
        j = 4 * (r_in % 4) + 2
        tmp = SPNetwork.frw_MagicSquare(block_in, SPNetwork.MAGIC_SQUARES[r])
        return SPNetwork.B2LB(SPNetwork.binary_shift(SPNetwork.LB2B(tmp), j))

    @staticmethod
    def inv_P_round(block_in: str, r_in: int) -> str:
        r = r_in % 3
        j = -(4 * (r_in % 4) + 2)
        tmp = SPNetwork.B2LB(SPNetwork.binary_shift(SPNetwork.LB2B(block_in), j))
        return SPNetwork.inv_MagicSquare(tmp, SPNetwork.MAGIC_SQUARES[r])


    @staticmethod
    def frw_round_SP(block_in: str, key_in: str, r_in: int) -> str:
        inter = "".join(SBlock.frw_S_CaesarM(block_in[i * 4:(i + 1) * 4], key_in) for i in range(4))
        return SPNetwork.block_xor(SPNetwork.frw_P_round(inter, r_in), key_in)

    @staticmethod
    def inv_round_SP(block_in: str, key_in: str, r_in: int) -> str:
        inter = SPNetwork.inv_P_round(SPNetwork.block_xor(block_in, key_in), r_in)
        return "".join(SBlock.inv_S_CaesarM(inter[i * 4:(i + 1) * 4], key_in) for i in range(4))


    @staticmethod
    def frw_SPNet(block_in: str, key_set: list, r_in: int) -> str:
        block = block_in
        for i in range(r_in):
            block = SPNetwork.frw_round_SP(block, key_set[i], i)
        return block

    @staticmethod
    def inv_SPNet(block_in: str, key_set: list, r_in: int) -> str:
        block = block_in
        for i in range(r_in - 1, -1, -1):
            block = SPNetwork.inv_round_SP(block, key_set[i], i)
        return block
