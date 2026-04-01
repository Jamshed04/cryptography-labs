from numeric import NumericOps
from core import CoreCrypto
from blocks import BlockOps

# Генератор псевдослучайных чисел (lab3)
class PRNGEngine:
    @staticmethod
    def LCG_NEXT(state_in: int, coefs_in: list) -> int:
        a, c, m = coefs_in
        return (a * state_in + c) % m

    @staticmethod
    def compose_num(num1_in: int, num2_in: int, cont_in: int) -> int:
        arr1 = NumericOps.dec2bin(num1_in)
        arr2 = NumericOps.dec2bin(num2_in)
        arr3 = NumericOps.dec2bin(cont_in)
        arr = [arr1[i] * arr3[i] + arr2[i] * ((1 + arr3[i]) % 2) for i in range(20)]
        return NumericOps.bin2dec(arr)

    @staticmethod
    def CT_LCG_NEXT(state_in: list, set_in: list) -> tuple:
        first = PRNGEngine.LCG_NEXT(state_in[0], set_in[0])
        second = PRNGEngine.LCG_NEXT(state_in[1], set_in[1])
        control = PRNGEngine.LCG_NEXT(state_in[2], set_in[2])
        out = PRNGEngine.compose_num(first, second, control)
        return out, first, second, control

    @staticmethod
    def seed2nums(array_in: list) -> list:
        return [NumericOps.block2num(x) for x in array_in]

    @staticmethod
    def initilize_PRNG(seed_in: str) -> list:
        cnst = [
            "ПЕРВОЕ_АКТЕРСТВО",
            "ВТОРОЙ_ДАЛЬТОНИК",
            "ТРЕТЬЯ_САДОВНИЦА",
            "ЧЕТВЕРТЫЙ_ГОБЛИН",
        ]
        value = [CoreCrypto.C_block([cnst[i], seed_in], "16") for i in range(4)]
        secret = CoreCrypto.C_block(value, "16")
        out = [None] * 4
        for i in range(4):
            tmp = value[i]
            TMP = ""
            for _ in range(4):
                tmp = BlockOps.add_txt(tmp, cnst[i])
                TMP += CoreCrypto.C_block([tmp, secret], "4")
                tmp = BlockOps.add_txt(tmp, TMP)
            out[i] = TMP[4:16]
        return out

    @staticmethod
    def C_CT_LSG_NEXT(init_flag: str, state_in, seed_in, set_in: list) -> tuple:
        stream = ""
        state = [None] * 4

        if init_flag == "up":
            init = PRNGEngine.initilize_PRNG(seed_in)
            for i in range(4):
                state[i] = PRNGEngine.seed2nums(
                    [init[i][0:4], init[i][4:8], init[i][8:12]]
                )
        elif init_flag == "down":
            state = state_in
        else:
            return "something_wrong", state

        for j in range(4):
            tmp, sign = 0, 1
            for i in range(4):
                T = PRNGEngine.CT_LCG_NEXT(state[i], set_in[j])
                state[i] = list(T[1:4])
                tmp = (1048576 + sign * T[0] + tmp) % 1048576
                sign = -sign
            stream += NumericOps.num2block(tmp)

        return stream, state