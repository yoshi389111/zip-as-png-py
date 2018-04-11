#!/usr/bin/env python3
# Copyright (C) 2018, SATO_Yoshiyuki
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php

'''ZIPファイルをPNGファイルに偽装します'''

import struct
import binascii


# PNGヘッダとIHDRの前半部分
_HEAD_PNG = bytes.fromhex("89504e470d0a1a0a0000000d49484452")
_SIZE_PNG_HEAD_IHDR = 8 + 4 + 4 + 0x0d + 4 # PNGヘッダ+IHDRのサイズ

_SIG_CEN = 0x02014b50 # CENのシグネチャ
_SIG_EOCD = bytes.fromhex('504b0506') # EOCDのシグネチャ
_SIZE_ZIP_CEN = 46 # CENの固定長部分のサイズ

_ZIP_ENDSIZ = 12 # EOCD内のCENの全体長のoffset
_ZIP_ENDOFF = 16 # EOCD内のCENのオフセットのoffset
_ZIP_CENNAM = 28 # CEN内のファイル名サイズのoffset
_ZIP_CENEXT = 30 # CEN内の拡張情報サイズのoffset
_ZIP_CENCOM = 32 # CEN内のコメントサイズのoffset
_ZIP_CENOFF = 42 # CEN内のLOCのoffset

# ZIPコンテナ格納時の補正するoffset
_OFFSET_ZIP = _SIZE_PNG_HEAD_IHDR + 4 + 4


def disguise(zip_buff: bytearray, png_buff: bytearray) -> bytearray:
    '''偽装コンテンツを作成

    :param zip_buff: ZIPファイルコンテンツ
    :param png_buff: PNGファイルコンテンツ
    :return: 偽装コンテンツ
    '''
    if png_buff[0:len(_HEAD_PNG)] != _HEAD_PNG:
        raise RuntimeError("Invalid PNG Header")
    if png_buff.find(_SIG_EOCD) != -1:
        raise RuntimeError("contains EOCD in PNG")
    pos_eocd = zip_buff.rfind(_SIG_EOCD)
    if pos_eocd == -1:
        raise RuntimeError("SIG_EOCD not found")

    pos_cen = struct.unpack_from("<I", zip_buff, pos_eocd + _ZIP_ENDOFF)[0]
    if pos_eocd <= pos_cen:
        raise RuntimeError("invalid order CEN and EOCD")
    if _SIG_CEN != struct.unpack_from("<I", zip_buff, pos_cen)[0]:
        raise RuntimeError("SIG_CEN not found")

    # CENの全体長を求める
    size_cen = struct.unpack_from("<I", zip_buff, pos_eocd + _ZIP_ENDSIZ)[0]

    # PNGヘッダ + IHDRチャンク
    out_1 = png_buff[0:_SIZE_PNG_HEAD_IHDR]

    # ZIPコンテナの長さ・チャンク名
    out_2 = bytearray()
    out_2.extend(struct.pack(">I", len(zip_buff)))
    out_2.extend(b'ziPc')

    out_3 = bytearray(zip_buff)

    # CENの中のLOCのオフセットを書き換える
    size = 0
    while size < size_cen:
        position = pos_cen + size
        offsetLoc = struct.unpack_from("<I", out_3, position + _ZIP_CENOFF)[0]
        struct.pack_into("<I", out_3, position + _ZIP_CENOFF, offsetLoc + _OFFSET_ZIP)
        cennam = struct.unpack_from("<I", out_3, position + _ZIP_CENNAM)[0]
        cenext = struct.unpack_from("<I", out_3, position + _ZIP_CENEXT)[0]
        cencom = struct.unpack_from("<I", out_3, position + _ZIP_CENCOM)[0]
        size += _SIZE_ZIP_CEN + cennam + cenext + cencom

    # EOCDの中のCENのオフセットを書き換える
    struct.pack_into("<I", out_3, pos_eocd + _ZIP_ENDOFF, pos_cen + _OFFSET_ZIP)

    # ZIPコンテナのCRCを出力
    crc1 = binascii.crc32(out_2[4:8])
    crc2 = binascii.crc32(out_3, crc1)
    out_4 = struct.pack(">I", crc2 & 0xffffffff)

    # PNGのIHDRチャンクより後ろ
    out_5 = png_buff[_SIZE_PNG_HEAD_IHDR:]

    out_buff = bytearray()
    out_buff.extend(out_1)
    out_buff.extend(out_2)
    out_buff.extend(out_3)
    out_buff.extend(out_4)
    out_buff.extend(out_5)
    return out_buff


def disguise_file(zip_file: str, png_file: str, out_file: str):
    '''偽装ファイル生成

    :param zip_file: ZIPファイル名
    :param png_file: PNGファイル名
    :param out_file: 出力ファイル名
    '''
    with open(zip_file, "rb") as zip, \
         open(png_file, "rb") as png, \
         open(out_file, "wb") as out:
       # ZIPファイルを読み込む
       zip_buff = zip.read()
       # PNGファイルを読み込む
       png_buff = png.read()
       # 偽装する
       out_buff = disguise(zip_buff, png_buff)
       # 偽装結果を出力
       out.write(out_buff)

 
if __name__ == "__main__":
    import sys
    argc = len(sys.argv)
    if argc != 4:
        raise RuntimeError("usage: zipaspng ZIP-FILE PNG-FILE OUT-FILE")
    disguise_file(sys.argv[1], sys.argv[2], sys.argv[3])
