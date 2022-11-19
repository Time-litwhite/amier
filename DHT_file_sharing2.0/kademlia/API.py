import asyncio
import functools
import logging
import os
import pickle

import aiofiles

from kademlia.file_split import ValueGenerator
from kademlia.network import Server
from kademlia.utils import get_ip, str_to_bytes, config

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


class API:
    def __init__(self):
        self.server = None
        self.frm = None

    async def initialize(self, frm, ip=get_ip()):
        """
        用已有的缓存文件直接初始化或手动初始化本机节点
        @param frm: UI框架
        @param ip: 本机ip地址
        @returns:Server实例对象
        """
        # 初始化本机节点
        self.frm = frm
        cache_file = config.cache_file
        try:
            if os.path.exists(cache_file):
                self.server = await Server.load_state(cache_file, 8888, ip)
            else:
                self.server = Server()
                listen_task = asyncio.create_task(self.server.listen(8888, ip))
                await listen_task
        except:
            log.error("Initialization exception, please try again!")
            return

    def _split_single_file(self, path):
        split = ValueGenerator(source_path=path)
        # file_hash显示在文件的下方 or 用户在赋值CID时取得
        file_hash = split.split_single_file(storage=self.server.storage)
        return file_hash

    async def _upload(self, file_hash):
        """
        上传文件

        :param(bytes) file_hash: 待上传的文件的分片列表
        :return:
        """
        # tasks = set()
        # for value in value_list:
        #     key = str_to_bytes(value.hash)
        #     value = value.pack_value()
        #     task = asyncio.create_task(self.server.set(key, value))
        #     tasks.add(task)
        #     task.add_done_callback(tasks.discard)
        # while tasks:
        #     await asyncio.sleep(0)
        value = self.server.storage[file_hash].pack_value()
        asyncio.create_task(self.server.set(file_hash, value))
        log.info("Upload finished!")

    def upload(self, file_hash):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self._upload(file_hash), loop=loop)

    async def find_chunks(self, torrent_hash):
        """
        根据所知道的种子文件的hash值(str)，从本节点server开始在network里查找拥有此种子的节点
        """
        # 将torrent_hash转换为bytes类型
        torrent_hash = str_to_bytes(torrent_hash)
        result = await self.server.get(torrent_hash)
        return result

    async def get_hash_list(self, hash_list):
        cnt = 0
        total_num = len(hash_list)
        batch = total_num
        if total_num > 500:
            batch = int(255 - 0.05 * total_num)
        current_num = {'n': 0}
        background_tasks = set()
        for key in hash_list:
            # key为完整的hash（bytes类型）
            cnt += 1
            if cnt == batch:
                await asyncio.sleep(2)
                cnt = 0
            task = asyncio.create_task(self.server.get(key))
            background_tasks.add(task)
            task.add_done_callback(functools.partial(self.add, current_num, background_tasks))
        while current_num['n'] < total_num:
            await asyncio.sleep(0)

    def add(self, dic, tasks, task):
        tasks.discard(task)
        dic['n'] += 1
        print(str(dic['n']) + "*"*20)

    # From UI Torrent_hash In method 'HashSearch'
    async def _download(self, torrent_hash):
        event = asyncio.Event()
        try:
            res = await self.find_chunks(torrent_hash)
            # 没有在network中找到种子文件
            if not res:
                raise NotImplemented
            # 此时本地已经从存在种子文件的节点处得到了该种子，并保存在~.\share目录下
            if not res.torrent_flag:
                # 待下载的文件大小小于256KB，则直接将其写入
                single_file_path = res.path
                desfile = config.download_path
                with open(os.path.join(desfile, res.hash), 'wb') as download_file:
                    with open(single_file_path, 'rb') as single_file:
                        download_file.write(single_file.read())
                    single_file.close()
                download_file.close()
                log.info("Download finished!")
                return

            torrent_path = res.path
            with open(torrent_path, 'rb') as torrent:
                # 将所有分片的hash值（bytes类型）读出，保存在piece_hashlist
                piece_hashlist = []
                piece_hash = torrent.read(20)
                while piece_hash:
                    piece_hashlist.append(piece_hash)
                    piece_hash = torrent.read(20)
            torrent.close()
            # 计算待下载的文件的大小/MB
            total_num = len(piece_hashlist)

            # 在network里查找存储着各个分片的hash的节点，从这些节点里下载各个分片
            cnt = 0
            batch = total_num
            if total_num > 500:
                batch = int(255 - 0.05 * total_num)
            current_num = {'n': 0}
            background_tasks = set()
            for key in piece_hashlist:
                # key为完整的hash（bytes类型）
                cnt += 1
                if cnt == batch:
                    await asyncio.sleep(2)
                    cnt = 0
                task = asyncio.create_task(self.server.get(key))
                background_tasks.add(task)
                task.add_done_callback(
                    functools.partial(self.frm.Page3_file.Download_Gauge.progress, total_num, background_tasks,
                                        current_num))
            waiter_task = asyncio.create_task(self.merge(event, piece_hashlist, torrent_hash))
            while current_num['n'] < total_num:
                await asyncio.sleep(0)
            event.set()
            # 所有分片下载完成后进行合并
            await waiter_task
        except KeyboardInterrupt:
            print("Download failed!")
        except NotImplemented:
            print("Download torrent failed!")
        finally:
            return

    def download(self, torrent_hash):
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self._download(torrent_hash), loop=loop)

    # 合并分片成为完整文件
    async def merge(self, event, download_order, torrent_hash):
        """
        :param event:
        :param(list[bytes]) download_order: 按照分片合并的顺序排列的piece_hash
        :param(str) torrent_hash: 种子文件hash
        :param desfile: 指定的保存下载文件的路径
        :return: None
        """
        await event.wait()
        await asyncio.sleep(0)
        print("*"*50)
        invalid_list = self.check_valid(download_order)
        await self.get_hash_list(invalid_list)
        # 根据download_order的顺序，将下载到的分片合并到一个完整文件
        # await asyncio.sleep(0.01)
        desfile = config.download_path
        async with aiofiles.open(os.path.join(desfile, torrent_hash), 'wb') as output:
            for eachfile in download_order:
                filepath = value = self.server.storage[eachfile]
                async with aiofiles.open(filepath, 'rb') as infile:
                    data = await infile.read()
                    await output.write(data)
                await infile.close()
        await output.close()
        log.info("Download finished!")

    def check_valid(self, download_order):
        """
        返回仍未收到分片的hash列表
        """
        invalid = []
        for piece_hash in download_order:
            if not self.server.storage[piece_hash].valid:
                invalid.append(piece_hash)
        return invalid

    # TO UI List[id,ip] File:'Node' as node_list #
    def show_peers(self):
        """
        find_neighbors找到自己长度为alpha的node邻居列表

        :return: 返回邻居的(id,ip)列表
        """
        neighbors = self.server.protocol.router.find_neighbors(self.server.node, self.server.alpha)
        return [(node.id.hex(), node.ip) for node in neighbors]

    # TO UI 自身IP，ID File:'Status' as ()
    def show_status(self):
        """
        提供本机节点的信息

        :return: node_id string类型, 已上传的文件大小
        """
        node_id = self.server.node.id.hex()
        node_ip = get_ip()
        return node_id, node_ip

    #
    def add_connection(self, ip):
        """
        :param ip:待连接节点的ip
        :return:
        """
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.server.bootstrap([(ip, 8888)]), loop=loop)

    # To UI File:'Status' as ()
    @staticmethod
    def get_uploaded_size():
        """
        :return:返回已上传文件的大小(已托管文件大小)
        """
        size = 0
        for root, dirs, files in os.walk(config.save_path):
            if 'share' in root:
                continue
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        return round(size, 2)

    # From UI File:'Set' ()

    @staticmethod
    def modify_Configuration_save(save_path):
        """
        修改配置文件
        """
        if save_path is not config.save_path:
            config._save_path = save_path  # 存储分片
        data = {
            'save_path': save_path,
            'download_path': config.download_path
        }
        with open(config.config_path, 'wb') as file:
            pickle.dump(data, file)

    @staticmethod
    def modify_Configuration_download(download_path):
        """
        修改配置文件
        """
        if download_path is not config.download_path:
            config._download_path = download_path  # 存储分片
        data = {
            'save_path': config.save_path,
            'download_path': download_path
        }
        with open(config.config_path, 'wb') as file:
            pickle.dump(data, file)

    # Do Before Close The exe
    async def exit(self):
        self.server.save_state(config.cache_file)
        self.server.stop()
