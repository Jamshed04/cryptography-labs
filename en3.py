import re
from operator import invert

from alphabet import AlphabetOps
from hashfunc import HashFunc
from alphabet import AlphabetOps
from blocks import BlockOps
from caesar import CaesarCipher
from sblock import SBlock
from core import CoreCrypto
from numeric import NumericOps
from prng import PRNGEngine
from spnet import SPNetwork


def KDF(
    MAT_IN: str,
    SALT_IN: str,
    CON_IN: list[str],
    SIZE_IN: list[int],
    iter_in: int,
):
    tmp = MAT_IN + SALT_IN

    for _ in range(iter_in + 1):
        ext = HashFunc.MerDam_hash(tmp)
        tmp = ext + tmp

    PRK = tmp
    out = []

    for i in range(len(SIZE_IN)):
        q = (SIZE_IN[i] + 63) // 64

        rem = i
        res = ""

        while rem > 0:
            h = rem % 32
            res += AlphabetOps.num2sym(h)
            rem = (rem - h) // 32

        if q > 0:
            hash_val = PRK
            for _ in range(q):
                tmp = hash_val + CON_IN[i] + PRK
                hash_val = HashFunc.MerDam_hash(tmp)
                res = hash_val + res
        else:
            tmp = PRK + CON_IN[i] + PRK
            res = HashFunc.MerDam_hash(tmp)

        out_i = res[:SIZE_IN[i]]
        out.append(out_i)

    return out

# print(KDF("ЧЕЧЕТКА", "СЕАНС", ["СЕАНСОВЫЙ_КЛЮЧ", "КЛЮЧ_РАСПРЕДЕЛЕНИЯ_КЛЮЧЕЙ"], [32, 16], 2))
# print(KDF("ЧЕЧЕТКА", "АТЛЕТ", ["МАСТЕР_КЛЮЧ"], [120], 2))

def sym2bin(s_in):
    return ord(s_in) - 48


def isSym(s_in):
    C = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЬЭЮЯ_"

    if C.find(s_in) > -1:
        out = 1
    else:
        out = -1

    return out


def msg2bin(MSG_IN):
    M = len(MSG_IN)
    i = 0
    f = 0
    tmp = []

    while isSym(MSG_IN[i]) == 1:
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
            tmp.append(sym2bin(p))

    return tmp

test1 = "ГНОЛЛЫ_ПИЛИЛИ_ПЫЛЕСОС_ЛОСОСЕМ"
test2 = "ГНОЛЛЫ_ПИЛИЛИ_ПЫЛЕСОС_ЛОСОСЕМ1110011011011"
# print(msg2bin(test1))
# print(msg2bin(test2))

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

# print(bin2msg(msg2bin(test1)))
# print(bin2msg(msg2bin(test2)))
with open("inp.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

INPUTS_ARRAY = [line.strip() for line in lines]

with open("ad.txt", "r", encoding="utf-8") as r:
    lines1 = r.readlines()

ASSOCDATA_ARRAY = [re.findall(r'"([^"]*)"', line1) for line1 in lines1]


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


def check_padding(BINMSG_IN):
    BINS = list(BINMSG_IN)
    M = len(BINS)
    blocks = M // 80
    remainder = M % 80
    f = 0
    numblocks = 0
    padlength = 0

    if remainder == 0:
        tb = BINS[M - 20 : M]
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
                tb2 = BINS[M - padlength : M - 20]
                if tb2[0] == 1:
                    f = 1
                    for j in range(1, padlength - 20):
                        if tb2[j] == 1:
                            f = 0
                            break
    return [f, [numblocks, padlength]]


def pad_message(MSG_IN):
    BINS = msg2bin(MSG_IN)
    M = len(BINS)
    blocks = M // 80
    remainder = M % 80

    if remainder == 0:
        f = check_padding(BINS)[0]
    else:
        f = 1

    if f == 1:
        pad = produce_padding(remainder, blocks)
        BINS.extend(pad)

    return bin2msg(BINS)


def unpad_message(MSG_IN):
    BINS = msg2bin(MSG_IN)
    M = len(BINS)
    T = check_padding(BINS)

    if T[0] == 1:
        pl = T[1][1]
        tmp = BINS[0 : M - pl]
        return bin2msg(tmp)
    else:
        return MSG_IN


# IN = INPUTS_ARRAY[0]
# print(len(IN))
# print(len(msg2bin(IN)))
# INTER = pad_message(IN)
# print(len(INTER))
# print(len(msg2bin(INTER)))
# OUT = unpad_message(INTER)
# print(len(OUT))
# print(len(msg2bin(OUT)))

# IN1 = INPUTS_ARRAY[1]
# print(len(IN1))
# print(len(msg2bin(IN1)))
# tmp = check_padding(msg2bin(IN1))
# print(tmp)
#
# INTER1 = pad_message(IN1)
# print(len(INTER1))
# print(len(msg2bin(INTER1)))
# tmp = check_padding(msg2bin(INTER1))
# print(tmp)
#
# OUT = unpad_message(INTER1)
# print(len(OUT))
# print(len(msg2bin(OUT)))
# print(OUT == IN1)


def prepare_packet(DATA_IN, IV_in, MSG_IN):
    data = list(DATA_IN)
    iv   = BlockOps.add_txt("________________", IV_in)
    msg  = pad_message(MSG_IN)
    L    = len(msg2bin(msg))

    a = ""
    for _ in range(5):
        a = AlphabetOps.num2sym(L % 32) + a
        L //= 32

    if len(data) > 4:
        data[4] = a
    else:
        data.append(a)

    mac = ""
    return [data, iv, msg, mac]

def validate_packet(PACKET_IN):
    data, iv, msg, mac = PACKET_IN
    f  = 1
    t  = data[0][0]
    s  = data[0][1]
    ml = len(mac)

    if t != "Б":
        f = 0
    elif (s == "А" or s == "Б") and ml != 16:
        f = 0
    elif s == "_" and ml != 0:
        f = 0
    return f


def transmit(PACKET_IN):
    data, iv, msg, mac = PACKET_IN
    out = data[0] + data[1] + data[2] + data[3] + data[4]
    out = msg2bin(out + iv + msg + mac)
    return out


def recieve(STREAM_IN):
    p  = bin2msg(STREAM_IN)
    M  = len(p)
    type_ = p[0:2]
    sender = p[2:10]
    reciever = p[10:18]
    session = p[18:27]
    length = p[27:32]
    iv = p[32:48]

    L = 0
    for i in range(5):
        l = AlphabetOps.sym2num(length[i])
        L = 32 * L + l
    L = L // 5

    message = p[48:48 + L]
    mac = p[48 + L:M]

    return [[type_, sender, reciever, session, length], iv, message, mac]


# XTST = prepare_packet(ASSOCDATA_ARRAY[1], "КОЛЕСО", INPUTS_ARRAY[1])
# YTST = recieve(transmit(XTST))
# print(XTST[2] == YTST[2])
# Q = transmit(XTST)
# print(validate_packet(YTST))


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


# A1 = "ГОЛОВКА_КРУЖИТСЯ"
# A2 = "МЫШКА_БЫЛА_ЛИХОЙ"
# B1 = "СИНЕВАТАЯ_БОРОДА"
# B2 = "ЗЕЛЕНЫЙ_КОТОЗМИЙ"
#
# C1 = textxor(A1, A2)
# C2 = textxor(A1, B2)
# C11 = textxor(C1, A2)
# C12 = textxor(C1, A1)
# C21 = textxor(C2, A1)
# C22 = textxor(C2, A2)
#
# print(C1)
# print(C2)
# print(C11)
# print(C12)
# print(C21)
# print(C22)


def enc_CTR(MSG_IN, IV_IN, KEY_IN):
    R = 8
    m = len(MSG_IN) // 16
    IV_starter = IV_IN[0:12]
    IV_ender = "____"
    ctr = 0
    out = ""

    for i in range(m):
        IV_ender = NumericOps.num2block(ctr)
        IV = IV_starter + IV_ender
        keystream = SPNetwork.frw_SPNet(IV, KEY_IN, R)
        inp = MSG_IN[i * 16 : i * 16 + 16]
        out = out + textxor(inp, keystream)
        ctr = ctr + 1

    return out


# TST = INPUTS_ARRAY[0]
# IV1 = "АЛИСА_УМЕЕТ_ПЕТЬ"
# keyset = SPNetwork.produce_round_keys("СЕАНСОВЫЙ_КЛЮЧИК", 8)
# F_TEST1 = enc_CTR(TST, IV1, keyset)
# print(F_TEST1)


def mac_CBC(MSG_IN, IV_IN, KEY_IN):
    R = 8
    m = len(MSG_IN) // 16
    ctr = 0
    out = ""
    feedback = IV_IN

    for i in range(m):
        inp = MSG_IN[i * 16 : i * 16 + 16]
        temp = textxor(feedback, inp)
        feedback = SPNetwork.frw_SPNet(temp, KEY_IN, R)
        out = out + feedback

    return feedback


# TST = INPUTS_ARRAY[0]
# IV1 = "АЛИСА_УМЕЕТ_ПЕТЬ"
# keyset = SPNetwork.produce_round_keys("СЕАНСОВЫЙ_КЛЮЧИК", 8)
# F_TEST1 = mac_CBC(TST, IV1, keyset)
# print(F_TEST1)


def combine(STRSET_IN):
    out = ""

    for i in range(len(STRSET_IN)):
        out += STRSET_IN[i]

    return out


def blockxor(A_IN, B_IN):
    A = NumericOps.dec2bin(NumericOps.block2num(A_IN))
    B = NumericOps.dec2bin(NumericOps.block2num(B_IN))

    C = [(A[j] + B[j]) % 2 for j in range(20)]

    c = NumericOps.bin2dec(C)

    return NumericOps.num2block(c)


# print(blockxor("КОНЬ", "А__Г"))
# print(blockxor("КОНЬ", "АБВГ"))
# print(blockxor("КОНЬ", "ЛУНЬ"))
# print(blockxor("КААА", "АБВГ"))


def CCM_frw(PACKET_IN, KEY_IN, onlymac):
    ASSDATA_IN, IV_IN, MSG_IN, tmp = PACKET_IN

    data = combine(ASSDATA_IN)
    M = len(MSG_IN)
    mac = mac_CBC(data + MSG_IN, IV_IN, KEY_IN)

    if onlymac == 0:
        msg = enc_CTR(MSG_IN + mac, IV_IN, KEY_IN)
        MSG = msg[0:M]
        MAC = msg[M:M + 16]
    else:
        MSG = MSG_IN
        MAC = mac

    return [ASSDATA_IN, IV_IN, MSG, MAC]


def CCM_inv(PACKET_IN, KEY_IN, onlymac):
    ASSDATA_IN, IV_IN, MSG_IN, MAC_IN = PACKET_IN

    data = combine(ASSDATA_IN)
    M = len(MSG_IN)

    if onlymac == 0:
        msg = enc_CTR(MSG_IN + MAC_IN, IV_IN, KEY_IN)
        MSG = msg[0:M]
        MAC = msg[M:M + 16]
    else:
        MSG = MSG_IN
        MAC = MAC_IN

    mac = mac_CBC(data + MSG, IV_IN, KEY_IN)
    MAC = textxor(MAC, mac)

    return [ASSDATA_IN, IV_IN, MSG, MAC]


# AD = ASSOCDATA_ARRAY[1]
# AD.append("АБВГД")
# print(AD)
# PACKET = [AD, "БОБ_НЕМНОГО_ПЬЯН", INPUTS_ARRAY[0], ""]
# keyset = SPNetwork.produce_round_keys("СЕАНСОВЫЙ_КЛЮЧИК", 8)
# Q_TEST1 = CCM_frw(PACKET, keyset, 0)
# print(Q_TEST1)
# R_TEST1 = CCM_inv(Q_TEST1, keyset, 0)
# print(R_TEST1)
# print(R_TEST1[2] == PACKET[2])
#
# Q_TEST0 = CCM_frw(PACKET, keyset, 1)
# print(Q_TEST0)
# R_TEST0 = CCM_inv(Q_TEST0, keyset, 1)
# print(R_TEST0)


def CCM(ASS_DATA, MSG_ARRAY, KEY_IN, nonce, type):
    mtype, sender, reciever, transmission = ASS_DATA

    t1 = reciever + sender
    t2 = mtype + transmission + "____"
    t3 = BlockOps.add_txt(t2, nonce)

    IV0 = (
        CoreCrypto.C_block([t1, t2], "4")
        + CoreCrypto.C_block([t3, t2, t1], "4")
        + "________"
    )

    msg_counter = -1
    keyset = SPNetwork.produce_round_keys(KEY_IN, 8)

    out = [None] * len(MSG_ARRAY)

    if type == "send":
        for i in range(len(MSG_ARRAY)):
            msg_sec = mtype
            msg_counter = msg_counter + 1
            IV1 = "________" + NumericOps.num2block(msg_counter) + "____"
            IV = textxor(IV0, IV1)

            tmp_packet = prepare_packet(
                [msg_sec, sender, reciever, transmission],
                IV,
                MSG_ARRAY[i]
            )

            if msg_sec == "В_":
                out[i] = transmit(tmp_packet)

            if msg_sec == "ВА":
                sec_packet = CCM_frw(tmp_packet, keyset, 1)
                out[i] = transmit(sec_packet)

            if msg_sec == "ВБ":
                sec_packet = CCM_frw(tmp_packet, keyset, 0)
                out[i] = transmit(sec_packet)

    if type == "recieve":
        last = -1
        for i in range(len(MSG_ARRAY)):
            tmp_packet = recieve(MSG_ARRAY[i])
            rdata = tmp_packet[0]
            x = tmp_packet[1][8:12]
            current = NumericOps.block2num(x)

            if current > last:
                if rdata[0] == "ВБ":
                    rec_packet = CCM_inv(tmp_packet, keyset, 0)
                    rec_packet[2] = unpad_message(rec_packet[2])
                    if rec_packet[3] == "________________":
                        last = current
                        rec_packet[3] = "ОК"

                elif rdata[0] == "ВА" and mtype != "ВБ":
                    rec_packet = CCM_inv(tmp_packet, keyset, 1)
                    rec_packet[2] = unpad_message(rec_packet[2])
                    if rec_packet[3] == "________________":
                        last = current
                        rec_packet[3] = "ОК"

                elif rdata[0] == "В_" and mtype == "В_":
                    rec_packet = tmp_packet
                    rec_packet[2] = unpad_message(rec_packet[2])
                    if rec_packet[3] == "":
                        last = current
                        rec_packet[3] = "N/A"

                else:
                    rec_packet = tmp_packet

                out[i] = rec_packet

    return out

# AD = ASSOCDATA_ARRAY[3]
# MESSAGES = INPUTS_ARRAY
# CHANNEL = CCM(AD, MESSAGES, "СЕАНСОВЫЙ_КЛЮЧИК", "СЕМИХАТОВ_КВАНТЫ", "send")
# CH = []
# for i in range(0, len(CHANNEL)):
#     l = CHANNEL[i]
#     CH.append(len(l))
#
# print(CH)
#
# CH0 = CHANNEL[0]
# CH3 = CHANNEL[3]
#
# CHANNEL[0][317] = 1 - CHANNEL[0][317]
# CHANNEL[3][12] = 1 - CHANNEL[3][12]
#
# TRANSMISSION = CCM(AD, CHANNEL, "СЕАНСОВЫЙ_КЛЮЧИК", "СЕМИХАТОВ_КВАНТЫ", "recieve")
# TR = []
# for i in range(0, len(TRANSMISSION)):
#     l = TRANSMISSION[i]
#     TR.append(len(l))
#
# print(TR)
#
# print(TRANSMISSION[0][0])
# print(TRANSMISSION[1][0])
# print(TRANSMISSION[2][0])
# print(TRANSMISSION[3][0])
#
# print(TRANSMISSION[0][1])
# print(TRANSMISSION[1][1])
# print(TRANSMISSION[2][1])
# print(TRANSMISSION[3][1])
#
# print(TRANSMISSION[0][2])
# print(TRANSMISSION[1][2])
# print(TRANSMISSION[2][2])
# print(TRANSMISSION[0][2] == MESSAGES[0], TRANSMISSION[1][2] == MESSAGES[1], TRANSMISSION[2][2] == MESSAGES[2])
# print(TRANSMISSION[3][2] == MESSAGES[3], TRANSMISSION[4][2] == MESSAGES[4], TRANSMISSION[5][2] == MESSAGES[5])
# print(msg2bin(TRANSMISSION[3][2]) == msg2bin(MESSAGES[3]))
# print(TRANSMISSION[0][3], TRANSMISSION[1][3], TRANSMISSION[2][3], TRANSMISSION[3][3])