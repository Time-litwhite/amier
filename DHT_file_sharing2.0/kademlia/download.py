import asyncio
import logging
import os
import string

from network import Server
from utils import Config, str_to_bytes

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger('')
log.addHandler(handler)
log.setLevel(logging.DEBUG)


async def run(torrent=None):
    server = Server()
    loop = asyncio.get_running_loop()
    loop.set_debug(True)

    asyncio.create_task(server.listen(8888, '10.12.62.93'))

    result = find_chunks(server=server, torrent_hash=torrent)
    if result:
        await download_chunks(server=server, torrent_hash=torrent)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
        loop.close()


def find_chunks(server, torrent_hash):
    """
    根据所知道的种子文件的hash值(str)，从本节点server开始在network里查找拥有此种子的节点
    """
    # 将torrent_hash转换为bytes类型
    torrent_hash = str_to_bytes(torrent_hash)
    result = server.get(torrent_hash)
    return result
    # if result:
    # 如果返回值不为空，则说明network里存在此文件信息，可用于下载
    # download_chunks(server, torrent_hash)


# 下载分片
async def download_chunks(server, torrent_hash):
    # 此时本地已经从存在种子文件的节点处得到了该种子，并保存在~.\share目录下
    torrent_path = os.path.join(Config.save_path, 'share', torrent_hash)
    download_order = []
    with open(torrent_path, 'r') as torrent:
        # 将分片的hash值读出
        piece_hashlist = torrent.readlines()
        # 在network里查找存储着各个分片的hash的节点，从这些节点里下载各个分片
        # 将每一个分片hash值转换为bytes类型
        cos = list(map(server.get, [str_to_bytes(key) for key in piece_hashlist[:-1]]))
        gathered = await asyncio.gather(*cos)
        print(gathered)

        # 记录各个分片的合并顺序
        for piece_hash in piece_hashlist[:-1]:
            download_order.append(piece_hash[:10])
    # 所有分片下载完成后进行合并
    merge(download_order)


# 合并分片成为完整文件
def merge(download_order, desfile=Config.download_path):
    # 根据download_order的顺序，将下载到的分片合并到desfile文件
    with open(desfile + 'downloadfile', 'wb') as output:
        for eachfile in download_order:
            filepath = os.path.join(Config.save_path, 'share', eachfile)
            with open(filepath, 'rb') as infile:
                data = infile.read()
                output.write(data)


if __name__ == "__main__":
    asyncio.run(run())
