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