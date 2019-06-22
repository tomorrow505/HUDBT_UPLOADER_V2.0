# -*- coding: utf-8 -*-
# Author:Chengli

import hashlib
import bencode
import os


def parse_blist(bdata):
    """ Convert bencoded data to python list """

    blist = []

    if bdata[0:1] == b'l':
        bdata = bdata[1:]

    while bdata[0:1] != b'' and bdata[0:1] != b'e':
        parse_func = btype_dict.get(bdata[0:1], parse_bstring)
        elem, bdata = parse_func(bdata)

        blist.append(elem)

    return blist, bdata[1:]


def parse_bdict(bdata):
    """ Convert bencoded data to python dict """

    bdict = {}

    if bdata[0:1] == b'd':
        bdata = bdata[1:]

    while bdata[0:1] != b'' and bdata[0:1] != b'e':

        parse_func = btype_dict.get(bdata[0:1], parse_bstring)
        key, bdata = parse_func(bdata)

        if bdata[0:1] == '' or bdata[0:1] == 'e':
            value = None
        else:
            parse_func = btype_dict.get(bdata[0:1], parse_bstring)
            value, bdata = parse_func(bdata)

        if key in bdict:
            raise KeyError("Multiple keys in bencoded dictionary")

        bdict[key] = value

    return bdict, bdata[1:]


def parse_bint(bdata):
    """ Convert bencoded data to int """

    end_pos = bdata.index(ord('e'))
    num_str = bdata[1:end_pos]
    bdata = bdata[end_pos + 1:]

    return int(num_str), bdata


def parse_bstring(bdata):
    """ Convert bencoded data to string """

    delim_pos = bdata.index(ord(':'))
    length = bdata[0:delim_pos]
    length = int(length)

    delim_pos += 1
    bstring = bdata[delim_pos:delim_pos + length]
    bdata = bdata[delim_pos + length:]

    if len(bstring) != length:
        raise ValueError("Incorrect bencoded string length")

    return bstring, bdata


def decode(bdata):
    """ Parse data and return a list of objects """

    return parse_blist(bdata)[0]


btype_dict = {
    b'd': parse_bdict,
    b'l': parse_blist,
    b'i': parse_bint
}


def sha1sum(src):
    if not len(src):
        return ""
    m = hashlib.sha1(src)
    return m.hexdigest()


def get_hash(filename):
    with open(filename, 'rb') as f:
        torrent_data = f.read()
        if -1 != torrent_data.find(b"nodes"):
            info_data = torrent_data[torrent_data.find(b"info") + 4:torrent_data.find(b"nodes") - 2]
        else:
            info_data = torrent_data[torrent_data.find(b"info") + 4:len(torrent_data) - 1]

        sha1_data = sha1sum(info_data)
    return sha1_data.upper()


# 馒头下下来是http，换成https
def change_tracker(torrent_path):
    back_path = torrent_path + '.torrent'
    os.rename(torrent_path, back_path)
    data = bencode.bread(back_path)
    data["announce"] = data["announce"].replace('http', 'https')
    bencode.bwrite(data, torrent_path)
    os.remove(back_path)


# if __name__ == "__main__":
#     path = r'E:\test\cache\The Cakemaker 2017 720p BluRay DD5 1 x264-BMDru_mteam_298549.torrent'
#     change_tracker(path)

