import os
import shutil

from kademlia.utils import Config, digest, str_to_bytes, config

kilobytes = 1024
chunksize = int(256 * kilobytes)  # default chunksize

"""
约定：
network中get和set方法中的key为string类型
set_digest中的key为bytes类型
crawling中的ValueSpiderCrawl,查找分片时只能通过创建一个node(id),而id为int类型
以下的讨论主体都是不同形式的hash
string转bytes：bytes(str,'utf-8')
bytes转string：str.hex()
string转int，int(string,16)
"""


# 节点保存的value定义如下：
class Value:
    def __init__(self, path, torrent_flag=False, hash=None, valid=False):
        """
        @param
        hash:分片/种子的hash值
        path:文件/种子存储路径
        torrent_flag:false表示value为分片,true表示该value为种子
        """
        self.hash = hash
        self.path = path
        self.torrent_flag = torrent_flag
        self.valid = valid

    def is_torrent(self):
        """
        返回是否为种子信息
        """
        return self.torrent_flag

    def single_verification(self, piece_hash):
        """
        用于验证下载得到的分片的正确性
        piece_hash:下载分片时，利用分片得到的hash
        """
        if not self.torrent_flag:
            return self.hash == piece_hash

    def pack_value(self):
        flag = 'False'
        if self.torrent_flag:
            flag = 'True'
        return self.path + '_' + flag + '_' + self.hash

    @staticmethod
    def unpack_value(string):
        value_list = string.split('_')
        value = Value(value_list[0], value_list[1] == 'True', value_list[2])
        return value

    @staticmethod
    def unpack_local_value(string):
        value_list = string.split('_')
        value = Value(value_list[0], value_list[1] == 'True', value_list[2], True)
        return value


class ValueGenerator:
    """
    value生成器将单个文件分片，并将value并保存在传入的storage
    """

    def __init__(self, source_path, block_size=chunksize):
        """
        @param:
        source_path: 本地上传文件时，待分片的文件路径
        block_size: 每个分片的大小，默认256K
        """
        self.source_path = source_path
        self.block_size = block_size

    def split_single_file(self, storage):
        """
        value.path为utils模块里Config类的save_path
        """
        # 用于返回给network，将该value上传到dht
        # value_list = []
        # 打开待分片文件
        input_file = open(self.source_path, 'rb')
        size = os.path.getsize(self.source_path)
        save_path = Config.save_path
        # 若单个文件的大小小于256kb，则直接存储在顶级目录save_path下
        # 也无需为此构建torrent
        if size <= chunksize:
            chunk = input_file.read()
            # chunk_hash为bytes类型
            chunk_hash = digest(chunk)
            # 将hash从bytes类型转换成字符串类型，取前10字节作为文件名称
            filename = os.path.join(config.save_path, chunk_hash.hex()[:10])
            value = Value(filename, False, chunk_hash.hex(), True)
            storage[chunk_hash] = value
            with open(filename, 'wb') as fileptr:
                fileptr.write(chunk)
            fileptr.close()
            return chunk_hash

        # 创建一个临时文件夹save_path/tmp,用于存储分片
        # 不能取文件的hash作为文件夹的名称，因为文件的hash只有最后才能得到
        hash_list = []
        file_path = os.path.join(config.save_path, 'tmp')  # 修改
        os.mkdir(file_path)

        while True:
            # 从文件中读取block_size大小的内容
            chunk = input_file.read(self.block_size)
            # check the chunk is empty
            if not chunk:
                break
            # 得到chunk的hash
            chunk_hash = digest(chunk)
            hash_list.append(chunk_hash)
            filename = os.path.join(file_path, chunk_hash.hex()[0:10])
            value = Value(filename, False, chunk_hash.hex(), True)
            storage[chunk_hash] = value
            with open(filename, 'wb') as fileobj:
                fileobj.write(chunk)
            fileobj.close()
        input_file.close()

        concat_hash = b''
        torrent_path = os.path.join(file_path, 'tmp')
        with open(torrent_path, 'ab') as torrent:
            # 将分片hash写进种子文件
            for piece_hash in hash_list:
                torrent.write(piece_hash)
                concat_hash += piece_hash
        torrent.close()
        # 得到最终的文件夹名
        file_hash = digest(concat_hash).hex()
        new_torrent_path = os.path.join(file_path, file_hash[:10])
        # 修改种子文件名，种子文件名可取全部位数
        os.rename(torrent_path, new_torrent_path)

        # 应该修改成的文件夹路径target
        target = os.path.join(config.save_path, file_hash[:10])
        # 判断是否已存在待上传文件
        if os.path.exists(target):
            shutil.rmtree(file_path)
            return None, None
        else:
            # 修改tmp文件夹名为file_hash
            os.rename(file_path, target)
            for hash in hash_list:
                # 修改每个分片的路径（不含种子），并加入value_list
                storage[hash].path = os.path.join(target, hash.hex()[:10])
            # 保存种子信息到storage
            key = str_to_bytes(file_hash)
            storage[key] = Value(os.path.join(target, file_hash[:10]), True, file_hash, True)
            return key


"""
对于小于256KB的文件，key为文件hash，分片的文件名为hash前10位
对于大于256KB的文件，key为文件hash，分片的文件名为hash前10位
先存储于tmp的文件夹中（file_hash无法事先得到）
存储在storage中，此时storage的key正确，value的path有问题（包含tmp）
文件分完片之后，得到hash_list
hash_list和file_hash写入torrent中，此时torrent文件名（可为tmp）待修改
将hash_list做拼接得到torrent的hash
此时修改torrent文件名
将storage中对应的value.path的文件名修正为torrent的hash前10位
将torrent加入storage
"""
