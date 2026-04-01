from alphabet import AlphabetOps

# Числовые операции (lab3)
class NumericOps:
    @staticmethod
    def block2num(block_in: str) -> int:
        if len(block_in) != 4:
            return "input_error"
        tmp = AlphabetOps.text2array(block_in)
        out, pos = 0, 1
        for i in reversed(range(4)):
            out += pos * tmp[i]
            pos *= 32
        return out

    @staticmethod
    def num2block(num_in: int) -> str:
        tmp = [0] * 4
        rem = num_in
        for i in range(4):
            tmp[3 - i] = rem % 32
            rem //= 32
        return AlphabetOps.array2text(tmp)

    @staticmethod
    def dec2bin(num_in: int) -> list:
        out = [0] * 20
        for i in range(20):
            out[19 - i] = num_in % 2
            num_in //= 2
        return out

    @staticmethod
    def bin2dec(bin_in: list) -> int:
        out = 0
        for b in bin_in:
            out = 2 * out + b
        return out
