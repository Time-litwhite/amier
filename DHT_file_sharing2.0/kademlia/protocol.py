import asyncio
import logging
import os
import random
import threading

import aiofiles
import nest_asyncio
from rpcudp.protocol import RPCProtocol

from kademlia.file_split import Value
from kademlia.node import Node
from kademlia.routing import RoutingTable
from kademlia.utils import digest, Config, config

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

nest_asyncio.apply()
storage_lock = asyncio.Lock()


class KademliaProtocol(RPCProtocol):
    def __init__(self, source_node, storage, ksize):
        RPCProtocol.__init__(self)
        self.router = RoutingTable(self, ksize, source_node)
        self.storage = storage  # 存储torrent文件的(key,value)信息
        self.source_node = source_node
        self.port_used_flag = [0] * Config.MAX_CONNECTION
        self.lock = asyncio.Lock()

    def get_refresh_ids(self):
        """
        Get ids to search for to keep old buckets up to date.
        """
        ids = []
        for bucket in self.router.lonely_buckets():
            rid = random.randint(*bucket.range).to_bytes(20, byteorder='big')
            ids.append(rid)
        return ids

    def rpc_stun(self, sender):  # pylint: disable=no-self-use
        return sender

    def rpc_ping(self, sender, nodeid):
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        return self.source_node.id

    def rpc_store(self, sender, nodeid, key, value):
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        if key not in self.storage.data or not self.storage[key].valid:
            log.debug("got a store request from %s, storing '%s'='%s'",
                        sender, key.hex(), value)
            # 保存其他节点发送来的分片的绝对路径
            value = Value.unpack_value(value)
            value.path = os.path.join(config.save_path, 'share', key.hex()[0:10])
            self.storage[key] = value
            return True
        log.debug("already exist the piece %s!", key.hex())
        return False

    def rpc_find_node(self, sender, nodeid, key):
        log.info("finding neighbors of %i in local table",
                 int(nodeid.hex(), 16))
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        node = Node(key)
        neighbors = self.router.find_neighbors(node, exclude=source)
        return list(map(tuple, neighbors))

    def rpc_find_value(self, sender, nodeid, key):
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        value = self.storage.get(key, None)
        if value is None:
            return self.rpc_find_node(sender, nodeid, key)
        value = value.pack_value()
        asyncio.ensure_future(self.call_store(source, key, value))
        return {'value': value}

    async def call_find_node(self, node_to_ask, node_to_find):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.find_node(address, self.source_node.id,
                                      node_to_find.id)
        return self.handle_call_response(result, node_to_ask)

    async def call_find_value(self, node_to_ask, node_to_find):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.find_value(address, self.source_node.id,
                                       node_to_find.id)
        return self.handle_call_response(result, node_to_ask)

    async def call_ping(self, node_to_ask):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.ping(address, self.source_node.id)
        return self.handle_call_response(result, node_to_ask)

    async def call_store(self, node_to_ask, key, value):
        async with storage_lock:
            value_obj = self.storage.get(key)
        if not value_obj.valid:
            return False, False
        else:
            address = (node_to_ask.ip, node_to_ask.port)
            result = await self.store(address, self.source_node.id, key, value)
            res = self.handle_call_response(result, node_to_ask)
            if res[1]:
                # 如果成功收到True的回复，则可以发送分片
                threading.Thread(self.send_piece(node_to_ask.ip, value)).start()
            return res

    def welcome_if_new(self, node):
        """
        Given a new node, send it all the keys/values it should be storing,
        then add it to the routing table.

        @param node: A new node that just joined (or that we just found out
        about).

        Process:
        For each key in storage, get k closest nodes.  If newnode is closer
        than the furtherst in that list, and the node for this server
        is closer than the closest in that list, then store the key/value
        on the new node (per section 2.5 of the paper)
        """
        if not self.router.is_new_node(node):
            return
        log.info("never seen %s before, adding to router", node)
        for key, value in self.storage:
            value = value.pack_value()
            keynode = Node(key)
            neighbors = self.router.find_neighbors(keynode)
            if neighbors:
                last = neighbors[-1].distance_to(keynode)
                new_node_close = node.distance_to(keynode) < last
                first = neighbors[0].distance_to(keynode)
                this_closest = self.source_node.distance_to(keynode) < first
            if not neighbors or (new_node_close and this_closest):
                asyncio.ensure_future(self.call_store(node, key, value))
        self.router.add_contact(node)

    def handle_call_response(self, result, node):
        """
        If we get a response, add the node to the routing table.  If
        we get no response, make sure it's removed from the routing table.
        """
        if not result[0]:
            log.warning("no response from %s, removing from router", node)
            self.router.remove_contact(node)
            return result
        log.info("got successful response from %s", node)
        self.welcome_if_new(node)
        return result

    # 发送分片内容
    def send_piece(self, target_ip, value):
        """
        @param target_ip:为远程主机的ip
        @param value:待发送分片
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        value_list = value.split('_')
        loop.run_until_complete(self.tcp_client(target_ip, value_list[0]))

    async def tcp_client(self, target_ip, path):
        # flag = False
        # port = 0
        port = random.randint(0, Config.MAX_CONNECTION - 1)
        # while not flag:
        #     port = random.randint(0, Config.MAX_CONNECTION - 1)
        #     async with self.lock:
        #         if self.port_used_flag[port] == 1:
        #             print('port:%d is used! path:%s will try again!', port, path)
        #             await asyncio.sleep(0)
        #         else:
        #             flag = True
        #             self.port_used_flag[port] = 1
        #             print('take port:%d! path:%s send successful', port, path)
        try:
            reader, writer = await asyncio.open_connection(
                target_ip, port + Config.start_port)
            async with aiofiles.open(path, 'rb') as file_ptr:
                writer.write(await file_ptr.read())
            await file_ptr.close()
            writer.write_eof()
            await writer.drain()
            # print("sending piece!")
            writer.close()

        except Exception as e:
            print(e)
            # await self.tcp_client(target_ip, path)
        finally:
            pass
            # async with self.lock:
            #     print("release port %d", port)
            #     self.port_used_flag[port] = 0
