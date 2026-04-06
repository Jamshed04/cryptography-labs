import re

from alphabet import AlphabetOps
from ccm import CCMProtocol
from blocks import BlockOps
from caesar import CaesarCipher
from sblock import SBlock
from core import CoreCrypto
from hashfunc import HashFunc
from numeric import NumericOps
from prng import PRNGEngine
from spnet import SPNetwork

def test_spnet():
    with open("inp.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    INPUTS_ARRAY = [line.strip() for line in lines]

    with open("ad.txt", "r", encoding="utf-8") as r:
        lines1 = r.readlines()

    ASSOCDATA_ARRAY = [re.findall(r'"([^"]*)"', line1) for line1 in lines1]

    AD = ASSOCDATA_ARRAY[3]
    MESSAGES = INPUTS_ARRAY
    CHANNEL = CCMProtocol.CCM(AD, MESSAGES, "СЕАНСОВЫЙ_КЛЮЧИК", "СЕМИХАТОВ_КВАНТЫ", "send")
    CH = []
    for i in range(0, len(CHANNEL)):
        l = CHANNEL[i]
        CH.append(len(l))

    print(CH)

    CHANNEL[0][317] = 1 - CHANNEL[0][317]
    CHANNEL[3][12] = 1 - CHANNEL[3][12]

    TRANSMISSION = CCMProtocol.CCM(AD, CHANNEL, "СЕАНСОВЫЙ_КЛЮЧИК", "СЕМИХАТОВ_КВАНТЫ", "recieve")
    TR = []
    for i in range(0, len(TRANSMISSION)):
        l = TRANSMISSION[i]
        TR.append(len(l))

    print(TR)

    print(TRANSMISSION[0][0])
    print(TRANSMISSION[1][0])
    print(TRANSMISSION[2][0])
    print(TRANSMISSION[3][0])

    print(TRANSMISSION[0][1])
    print(TRANSMISSION[1][1])
    print(TRANSMISSION[2][1])
    print(TRANSMISSION[3][1])

    print(TRANSMISSION[0][2])
    print(TRANSMISSION[1][2])
    print(TRANSMISSION[2][2])
    print(TRANSMISSION[0][2] == MESSAGES[0], TRANSMISSION[1][2] == MESSAGES[1], TRANSMISSION[2][2] == MESSAGES[2])
    print(TRANSMISSION[3][2] == MESSAGES[3], TRANSMISSION[4][2] == MESSAGES[4], TRANSMISSION[5][2] == MESSAGES[5])
    print(CoreCrypto.msg2bin(TRANSMISSION[3][2]) == CoreCrypto.msg2bin(MESSAGES[3]))
    print(TRANSMISSION[0][3], TRANSMISSION[1][3], TRANSMISSION[2][3], TRANSMISSION[3][3])



if __name__ == "__main__":
    test_spnet()