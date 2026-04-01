class AlphabetOps:
    ALPHABET = "_АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯ"

    @staticmethod
    def num2sym(num: int) -> str:
        return AlphabetOps.ALPHABET[num % 32]

    @staticmethod
    def sym2num(sym: str) -> int:
        pos = AlphabetOps.ALPHABET.find(sym)
        return 0 if pos == -1 else pos

    @staticmethod
    def add_s(s1: str, s2: str) -> str:
        return AlphabetOps.num2sym(
            (AlphabetOps.sym2num(s1) + AlphabetOps.sym2num(s2)) % 32
        )

    @staticmethod
    def sub_s(s1: str, s2: str) -> str:
        return AlphabetOps.num2sym(
            (AlphabetOps.sym2num(s1) - AlphabetOps.sym2num(s2) + 32) % 32
        )

    @staticmethod
    def text2array(text: str) -> list:
        return [AlphabetOps.sym2num(ch) for ch in text]

    @staticmethod
    def array2text(arr: list) -> str:
        return "".join(AlphabetOps.num2sym(n) for n in arr)