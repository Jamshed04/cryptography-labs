from blocks import BlockOps
from alphabet import AlphabetOps
from numeric import NumericOps
from core import CoreCrypto
from spnet import SPNetwork

class CCMProtocol:
    @staticmethod
    def prepare_packet(DATA_IN, IV_in, MSG_IN):
        data = list(DATA_IN)
        iv = BlockOps.add_txt("________________", IV_in)
        msg = CoreCrypto.pad_message(MSG_IN)
        L = len(CoreCrypto.msg2bin(msg))

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

    @staticmethod
    def validate_packet(PACKET_IN):
        data, iv, msg, mac = PACKET_IN
        f = 1
        t = data[0][0]
        s = data[0][1]
        ml = len(mac)

        if t != "Б":
            f = 0
        elif (s == "А" or s == "Б") and ml != 16:
            f = 0
        elif s == "_" and ml != 0:
            f = 0
        return f

    @staticmethod
    def transmit(PACKET_IN):
        data, iv, msg, mac = PACKET_IN
        out = data[0] + data[1] + data[2] + data[3] + data[4]
        out = CoreCrypto.msg2bin(out + iv + msg + mac)
        return out

    @staticmethod
    def recieve(STREAM_IN):
        p = CoreCrypto.bin2msg(STREAM_IN)
        M = len(p)
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

    @staticmethod
    def CCM_frw(PACKET_IN, KEY_IN, onlymac):
        ASSDATA_IN, IV_IN, MSG_IN, tmp = PACKET_IN

        data = BlockOps.combine(ASSDATA_IN)
        M = len(MSG_IN)
        mac = SPNetwork.mac_CBC(data + MSG_IN, IV_IN, KEY_IN)

        if onlymac == 0:
            msg = SPNetwork.enc_CTR(MSG_IN + mac, IV_IN, KEY_IN)
            MSG = msg[0:M]
            MAC = msg[M:M + 16]
        else:
            MSG = MSG_IN
            MAC = mac

        return [ASSDATA_IN, IV_IN, MSG, MAC]

    @staticmethod
    def CCM_inv(PACKET_IN, KEY_IN, onlymac):
        ASSDATA_IN, IV_IN, MSG_IN, MAC_IN = PACKET_IN

        data = BlockOps.combine(ASSDATA_IN)
        M = len(MSG_IN)

        if onlymac == 0:
            msg = SPNetwork.enc_CTR(MSG_IN + MAC_IN, IV_IN, KEY_IN)
            MSG = msg[0:M]
            MAC = msg[M:M + 16]
        else:
            MSG = MSG_IN
            MAC = MAC_IN

        mac = SPNetwork.mac_CBC(data + MSG, IV_IN, KEY_IN)
        MAC = BlockOps.textxor(MAC, mac)

        return [ASSDATA_IN, IV_IN, MSG, MAC]

    @staticmethod
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
                IV = BlockOps.textxor(IV0, IV1)

                tmp_packet = CCMProtocol.prepare_packet(
                    [msg_sec, sender, reciever, transmission],
                    IV,
                    MSG_ARRAY[i]
                )

                if msg_sec == "В_":
                    out[i] = CCMProtocol.transmit(tmp_packet)

                if msg_sec == "ВА":
                    sec_packet = CCMProtocol.CCM_frw(tmp_packet, keyset, 1)
                    out[i] = CCMProtocol.transmit(sec_packet)

                if msg_sec == "ВБ":
                    sec_packet = CCMProtocol.CCM_frw(tmp_packet, keyset, 0)
                    out[i] = CCMProtocol.transmit(sec_packet)

        if type == "recieve":
            last = -1
            for i in range(len(MSG_ARRAY)):
                tmp_packet = CCMProtocol.recieve(MSG_ARRAY[i])
                rdata = tmp_packet[0]
                x = tmp_packet[1][8:12]
                current = NumericOps.block2num(x)

                if current > last:
                    if rdata[0] == "ВБ":
                        rec_packet = CCMProtocol.CCM_inv(tmp_packet, keyset, 0)
                        rec_packet[2] = CoreCrypto.unpad_message(rec_packet[2])
                        if rec_packet[3] == "________________":
                            last = current
                            rec_packet[3] = "ОК"

                    elif rdata[0] == "ВА" and mtype != "ВБ":
                        rec_packet = CCMProtocol.CCM_inv(tmp_packet, keyset, 1)
                        rec_packet[2] = CoreCrypto.unpad_message(rec_packet[2])
                        if rec_packet[3] == "________________":
                            last = current
                            rec_packet[3] = "ОК"

                    elif rdata[0] == "В_" and mtype == "В_":
                        rec_packet = tmp_packet
                        rec_packet[2] = CoreCrypto.unpad_message(rec_packet[2])
                        if rec_packet[3] == "":
                            last = current
                            rec_packet[3] = "N/A"

                    else:
                        rec_packet = tmp_packet

                    out[i] = rec_packet

        return out