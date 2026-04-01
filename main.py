from alphabet import AlphabetOps
from blocks import BlockOps
from caesar import CaesarCipher
from sblock import SBlock
from core import CoreCrypto
from hashfunc import HashFunc
from numeric import NumericOps
from prng import PRNGEngine
from spnet import SPNetwork

def test_spnet():
    plain = "КОРЫСТЬ_СЛОНА_ЭХ"
    key_sp = "МТВ_ВСЕ_ЕЩЕ_ТЛЕН"

    keys = SPNetwork.produce_round_keys(key_sp, 8)
    cipher = SPNetwork.frw_SPNet(plain, keys, 8)
    deciph = SPNetwork.inv_SPNet(cipher, keys, 8)

    print("Открытый текст:", plain)
    print("Шифртекст:", cipher)
    print("Расшифровано:", deciph)
    print("Совпадает:", plain == deciph)



if __name__ == "__main__":
    test_spnet()