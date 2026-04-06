from alphabet import AlphabetOps
from blocks import BlockOps

# Ядро (lab2)
class CoreCrypto:
    @staticmethod
    def core_Caesar(prime: str, aux: str) -> str:
        C1 = [1, -1, 1, -1, 1, -1, 1]
        C2 = [1, -1, 1, -1, 1]
        prime = AlphabetOps.text2array(prime)
        aux = AlphabetOps.text2array(aux)
        arr = [0] * 16
        temp = 0
        t1 = sum(aux)
        c1 = t1 % 7
        c2 = prime[2 * c1 + 1] % 5
        c3 = (prime[2 * c2] + prime[2 * c1]) % 16
        for i in range(16):
            q = (c1 + i) % 7
            j = (c2 + i) % 5
            p = (c3 + i) % 16
            temp = (temp + 64 + prime[p] + C1[q] * aux[i % 16] * C2[j]) % 32
            arr[i % 16] = temp
        return AlphabetOps.array2text(arr)

    @staticmethod
    def confuse(s1: str, s2: str) -> str:
        a1 = AlphabetOps.text2array(s1)
        a2 = AlphabetOps.text2array(s2)
        res = [((a1[i] if a1[i] > a2[i] else a2[i]) + i) % 32 for i in range(16)]
        tmp = AlphabetOps.array2text(res)
        return BlockOps.add_txt(BlockOps.add_txt(tmp, s1), s2)

    @staticmethod
    def mixinputs(in_val: list) -> list:
        out1 = BlockOps.add_txt(in_val[0], in_val[1])
        out2 = BlockOps.sub_txt(in_val[0], in_val[1])
        out3 = BlockOps.add_txt(out2, BlockOps.add_txt(in_val[2], in_val[3]))
        out4 = BlockOps.add_txt(out1, BlockOps.sub_txt(in_val[2], in_val[3]))
        return [out1, out2, out3, out4]

    @staticmethod
    def C_block(arr: list, out_size: str) -> str:
        C = [
            "________________",
            "ПРОЖЕКТОР_ЧЕПУХИ",
            "КОЛЫХАТЬ_ПАРОДИЮ",
            "КАРМАННЫЙ_АТАМАН",
        ]
        flag = 1
        for i in range(len(arr)):
            if len(arr[i]) == 16:
                C[i] = BlockOps.add_txt(C[i], arr[i])
            else:
                flag = 0
        if not flag:
            return "input_error"
        C = CoreCrypto.mixinputs(C)
        tmp1 = CoreCrypto.core_Caesar(C[0], C[2])
        tmp2 = CoreCrypto.core_Caesar(C[3], C[1])
        tmp3 = CoreCrypto.confuse(tmp1, tmp2)
        out = CoreCrypto.core_Caesar(tmp3, tmp1)
        return BlockOps.compress(out, int(out_size))

    @staticmethod
    def sym2bin(s_in):
        return ord(s_in) - 48

    @staticmethod
    def isSym(s_in):
        C = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯ_"

        if C.find(s_in) > -1:
            out = 1
        else:
            out = -1

        return out

    @staticmethod
    def msg2bin(MSG_IN):
        M = len(MSG_IN)
        i = 0
        f = 0
        tmp = []

        while CoreCrypto.isSym(MSG_IN[i]) == 1:
            p = MSG_IN[i]
            c = AlphabetOps.sym2num(p)

            bits = []
            for j in range(5):
                bits.append(c % 2)
                c = c // 2
            bits.reverse()
            tmp.extend(bits)

            if i == M - 1:
                f = 1
                break
            else:
                i += 1

        if f == 0:
            for k in range(i, M):
                p = MSG_IN[k]
                tmp.append(CoreCrypto.sym2bin(p))

        return tmp

    @staticmethod
    def bin2msg(BIN_IN):
        B = len(BIN_IN)
        b = B // 5
        q = B % 5
        out = ""

        for i in range(b):
            t = 0
            for j in range(5):
                t = 2 * t + BIN_IN[i * 5 + j]
            out += AlphabetOps.num2sym(t)

        if q > 0:
            for k in range(1, q + 1):
                out += str(BIN_IN[b * 5 + k - 1])

        return out

    @staticmethod
    def produce_padding(rem_in, blocks_in):
        if rem_in == 0:
            b = blocks_in + 1
            r = 80
        elif rem_in <= 57:
            r = 80 - rem_in
            b = blocks_in + 1
        else:
            b = blocks_in + 2
            r = 160 - rem_in

        pad = [0] * r
        pad[0] = 1

        rt = r
        for i in range(6, -1, -1):
            pad[r - 20 + i] = rt % 2
            rt //= 2

        bt = b
        for i in range(9, -1, -1):
            pad[r - 13 + i] = bt % 2
            bt //= 2

        pad[r - 3] = 0
        pad[r - 2] = 0
        pad[r - 1] = 1
        return pad

    @staticmethod
    def check_padding(BINMSG_IN):
        BINS = list(BINMSG_IN)
        M = len(BINS)
        blocks = M // 80
        remainder = M % 80
        f = 0
        numblocks = 0
        padlength = 0

        if remainder == 0:
            tb = BINS[M - 20: M]
            ender = tb[17:20]

            if ender == [0, 0, 1]:
                NB = tb[7:17]
                PL = tb[0:7]

                padlength = 0
                for i in range(7):
                    padlength = 2 * padlength + PL[i]

                numblocks = 0
                for i in range(10):
                    numblocks = 2 * numblocks + NB[i]

                if numblocks == blocks and 23 <= padlength < 103:
                    tb2 = BINS[M - padlength: M - 20]
                    if tb2[0] == 1:
                        f = 1
                        for j in range(1, padlength - 20):
                            if tb2[j] == 1:
                                f = 0
                                break
        return [f, [numblocks, padlength]]

    @staticmethod
    def pad_message(MSG_IN):
        BINS = CoreCrypto.msg2bin(MSG_IN)
        M = len(BINS)
        blocks = M // 80
        remainder = M % 80

        if remainder == 0:
            f = CoreCrypto.check_padding(BINS)[0]
        else:
            f = 1

        if f == 1:
            pad = CoreCrypto.produce_padding(remainder, blocks)
            BINS.extend(pad)

        return CoreCrypto.bin2msg(BINS)

    @staticmethod
    def unpad_message(MSG_IN):
        BINS = CoreCrypto.msg2bin(MSG_IN)
        M = len(BINS)
        T = CoreCrypto.check_padding(BINS)

        if T[0] == 1:
            pl = T[1][1]
            tmp = BINS[0: M - pl]
            return CoreCrypto.bin2msg(tmp)
        else:
            return MSG_IN