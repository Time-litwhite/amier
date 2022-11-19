"""
General catchall for functions that don't make sense as methods.
"""
import asyncio
import binascii
import hashlib
import operator
import os
import pickle
import socket


async def gather_dict(dic):
    cors = list(dic.values())
    results = await asyncio.gather(*cors)
    return dict(zip(dic.keys(), results))


def digest(string):
    if not isinstance(string, bytes):
        string = str(string).encode('utf8')
    return hashlib.sha1(string).digest()


def shared_prefix(args):
    """
    Find the shared prefix between the strings.

    For instance:

        sharedPrefix(['blahblah', 'blahwhat'])

    returns 'blah'.
    """
    i = 0
    while i < min(map(len, args)):
        if len(set(map(operator.itemgetter(i), args))) != 1:
            break
        i += 1
    return args[0][:i]


def bytes_to_bit_string(bites):
    bits = [bin(bite)[2:].rjust(8, '0') for bite in bites]
    return "".join(bits)


def str_to_bytes(string):
    return binascii.unhexlify(string)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = (s.getsockname()[0])
    s.close()
    return ip


# class Config:
#     # 其他节点发送来的分片保存的根目录
#     save_path = '.\\save'
#     MAX_CONNECTION = 100
#     start_port = 50000
#     # 下载文件时默认保存路径
#     download_path = '.\\save'
#     cache_file = os.path.join(save_path, 'cache_file')


class Config:
    MAX_CONNECTION = 150
    start_port = 50000

    # 其他节点发送来的分片保存的根目录
    def __init__(self):
        self.config_path = "../config.txt"
        self._download_path = "../"
        self._save_path = "../save"
        self.cache_file = "../save/cache_file"
        self.get()

    def get(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'rb') as file:
                data = pickle.load(file)
                self._save_path = data["save_path"]
                # 下载文件时默认保存路径
                self._download_path = data["download_path"]
                self.cache_file = os.path.join(self._save_path, 'cache_file')

    @property
    def save_path(self):
        return self._save_path

    @property
    def download_path(self):
        return self._download_path


config = Config()
