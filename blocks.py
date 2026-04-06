from alphabet import AlphabetOps
from numeric import NumericOps

# Операции над блоками (lab2)
class BlockOps:
    @staticmethod
    def add_txt(t1: str, t2: str) -> str:
        m = min(len(t1), len(t2))
        longer = t1 if len(t1) >= len(t2) else t2
        result = ""
        for i in range(m):
            result += AlphabetOps.add_s(t1[i], t2[i])
        result += longer[m:]
        return result

    @staticmethod
    def sub_txt(t1: str, t2: str) -> str:
        n = min(len(t1), len(t2))
        r = "".join(
            AlphabetOps.num2sym(
                (AlphabetOps.sym2num(t1[i]) - AlphabetOps.sym2num(t2[i]) + 32) % 32
            )
            for i in range(n)
        )
        return r + (t1[n:] if len(t1) > n else "")

    @staticmethod
    def rev(txt: str) -> str:
        arr = AlphabetOps.text2array(txt)
        return AlphabetOps.array2text(list(reversed(arr)))

    @staticmethod
    def blocks_mix(a: str, b: str) -> list:
        b_rev = BlockOps.rev(a)
        return [BlockOps.add_txt(b_rev, b), BlockOps.sub_txt(b_rev, b)]

    @staticmethod
    def block_mask(s: str, con: str) -> str:
        a = AlphabetOps.text2array(s)
        c = AlphabetOps.text2array(con)
        res = [0] * 16
        for i in range(16):
            if a[i] < (c[i] + i):
                res[i] = (64 - (c[i] - i)) % 32
            else:
                res[i] = (a[i] + i) % 32
        return AlphabetOps.array2text(res)

    @staticmethod
    def compress(in_16: str, out_n: int) -> str:
        if out_n == 16:
            return in_16
        a1, a2, a3, a4 = in_16[0:4], in_16[4:8], in_16[8:12], in_16[12:16]
        if out_n == 8:
            return BlockOps.add_txt(a1 + a3, a2 + a4)
        if out_n == 4:
            return BlockOps.add_txt(BlockOps.sub_txt(a1, a3), BlockOps.sub_txt(a2, a4))
        return "input_error"

    @staticmethod
    def textxor(A_IN, B_IN):
        out = ""
        for i in range(4):
            a = A_IN[i * 4: i * 4 + 4]
            b = B_IN[i * 4: i * 4 + 4]

            A = NumericOps.dec2bin(NumericOps.block2num(a))
            B = NumericOps.dec2bin(NumericOps.block2num(b))

            C = [(A[j] + B[j]) % 2 for j in range(20)]

            out += NumericOps.num2block(NumericOps.bin2dec(C))
        return out

    @staticmethod
    def combine(STRSET_IN):
        out = ""

        for i in range(len(STRSET_IN)):
            out += STRSET_IN[i]

        return out

    @staticmethod
    def blockxor(A_IN, B_IN):
        A = NumericOps.dec2bin(NumericOps.block2num(A_IN))
        B = NumericOps.dec2bin(NumericOps.block2num(B_IN))

        C = [(A[j] + B[j]) % 2 for j in range(20)]

        c = NumericOps.bin2dec(C)

        return NumericOps.num2block(c)