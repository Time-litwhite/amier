import asyncio
import os
import pickle
import threading
import wx
import Introduction
import Set
import Files
import Status
import Node
import kademlia.API as KADE

from kademlia.utils import get_ip, config
import gl

# 存在cachefile时的做法， 第一次使用必定没有cachefile， node_id为随机生成
if os.path.exists(config.cache_file):
    with open(config.cache_file, 'rb') as file:
        data = pickle.load(file)
        node_id = data['id']
gl.node_ip = get_ip()


class Myframe(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(920, 600))

        self.loop = None
        self.A = KADE.API()
        self.Page1_about = None
        self.Page2_status = None
        self.Page3_file = None
        self.Page4_node = None
        self.Page5_set = None
        self.PageSizer = None
        PNG1 = wx.Bitmap('About.png')
        PNG1=PNG1.ConvertToImage()
        PNG1=PNG1.Scale(120,120)
        self.PNG_List = [PNG1, wx.Bitmap('Status.png'), wx.Bitmap('File.png'), wx.Bitmap('Node.png'),
                         wx.Bitmap('Set.png')]
        self.PNG_List2 = [PNG1, wx.Bitmap('Status2.png'), wx.Bitmap('File2.png'), wx.Bitmap('Node2.png'),
                          wx.Bitmap('Set2.png')]
        Splitter = wx.SplitterWindow(self, -1)
        self.panelLeft = wx.Panel(Splitter, -1)
        self.panelRight = wx.Panel(Splitter, -1)
        self.SetLeft()
        self.SetRight()
        self.Centre()
        self.Show(True)
        Splitter.SplitVertically(self.panelLeft, self.panelRight, 100)

    def SetLeft(self):
        # 设置左边窗口的值
        hbox1 = wx.GridSizer(5, 1, 0, 0)

        self.button1 = wx.BitmapButton(self.panelLeft, wx.ID_ANY, self.PNG_List[0])
        self.button1.Bind(wx.EVT_BUTTON, self.Switch1)
        hbox1.Add(self.button1, 0, wx.EXPAND)

        self.button2 = wx.BitmapButton(self.panelLeft, wx.ID_ANY, self.PNG_List[1])
        self.button2.Bind(wx.EVT_BUTTON, self.Switch2)
        hbox1.Add(self.button2, 0, wx.EXPAND)

        self.button3 = wx.BitmapButton(self.panelLeft, wx.ID_ANY, self.PNG_List[2])
        self.button3.Bind(wx.EVT_BUTTON, self.Switch3)
        hbox1.Add(self.button3, 0, wx.EXPAND)

        self.button4 = wx.BitmapButton(self.panelLeft, wx.ID_ANY, self.PNG_List[3])
        self.button4.Bind(wx.EVT_BUTTON, self.Switch4)
        hbox1.Add(self.button4, 0, wx.EXPAND)

        self.button5 = wx.BitmapButton(self.panelLeft, wx.ID_ANY, self.PNG_List[4])
        self.button5.Bind(wx.EVT_BUTTON, self.Switch5)
        hbox1.Add(self.button5, 0, wx.EXPAND)

        self.panelLeft.SetSizer(hbox1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def SetRight(self):
        self.PageSizer = wx.BoxSizer(wx.VERTICAL)
        self.Page1_about = Introduction.status(self.panelRight, self.A)
        self.Page2_status = Status.Link(self.panelRight, self.A)
        self.Page3_file = Files.File(self.panelRight, self.A)
        self.Page4_node = Node.node(self.panelRight, self.A)
        self.Page5_set = Set.set(self.panelRight, self.A)

        self.PageSizer.Add(self.Page1_about, 2, wx.EXPAND)
        self.PageSizer.Add(self.Page2_status, 2, wx.EXPAND)
        self.PageSizer.Add(self.Page3_file, 2, wx.EXPAND)
        self.PageSizer.Add(self.Page4_node, 2, wx.EXPAND)
        self.PageSizer.Add(self.Page5_set, 2, wx.EXPAND)
        self.Page2_status.Hide()
        self.Page3_file.Hide()
        self.Page4_node.Hide()
        self.Page5_set.Hide()
        self.panelRight.SetSizer(self.PageSizer)

    def Switch1(self, event):
        self.Page1_about.Show()
        self.Page2_status.Hide()
        self.Page3_file.Hide()
        self.Page4_node.Hide()
        self.Page5_set.Hide()
        self.button2.SetBitmap(self.PNG_List[1])
        self.button3.SetBitmap(self.PNG_List[2])
        self.button4.SetBitmap(self.PNG_List[3])
        self.button5.SetBitmap(self.PNG_List[4])
        self.PageSizer.Layout()

    def Switch2(self, event):
        self.Page1_about.Hide()
        self.Page2_status.Show()
        self.Page3_file.Hide()
        self.Page4_node.Hide()
        self.Page5_set.Hide()
        self.button2.SetBitmap(self.PNG_List2[1])
        self.button3.SetBitmap(self.PNG_List[2])
        self.button4.SetBitmap(self.PNG_List[3])
        self.button5.SetBitmap(self.PNG_List[4])
        self.PageSizer.Layout()

    def Switch3(self, event):
        self.Page1_about.Hide()
        self.Page2_status.Hide()
        self.Page3_file.Show()
        self.Page4_node.Hide()
        self.Page5_set.Hide()
        self.button2.SetBitmap(self.PNG_List[1])
        self.button3.SetBitmap(self.PNG_List2[2])
        self.button4.SetBitmap(self.PNG_List[3])
        self.button5.SetBitmap(self.PNG_List[4])
        self.PageSizer.Layout()

    def Switch4(self, event):
        self.Page1_about.Hide()
        self.Page2_status.Hide()
        self.Page3_file.Hide()
        self.Page4_node.Show()
        self.Page5_set.Hide()
        self.button2.SetBitmap(self.PNG_List[1])
        self.button3.SetBitmap(self.PNG_List[2])
        self.button4.SetBitmap(self.PNG_List2[3])
        self.button5.SetBitmap(self.PNG_List[4])
        self.PageSizer.Layout()

    def Switch5(self, event):
        self.Page1_about.Hide()
        self.Page2_status.Hide()
        self.Page3_file.Hide()
        self.Page4_node.Hide()
        self.Page5_set.Show()
        self.button2.SetBitmap(self.PNG_List[1])
        self.button3.SetBitmap(self.PNG_List[2])
        self.button4.SetBitmap(self.PNG_List[3])
        self.button5.SetBitmap(self.PNG_List2[4])
        self.PageSizer.Layout()

    def OnClose(self, e):
        dial = wx.MessageDialog(None, '确定要退出下载器吗？', '确认退出',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        ret = dial.ShowModal()
        if ret == wx.ID_YES:
            asyncio.run_coroutine_threadsafe(self.A.exit(), self.loop)
            # self.A.exit()
            self.Destroy()
        else:
            e.Veto()


def launch(frm):
    asyncio.set_event_loop(loop)
    loop.set_debug(True)
    loop.run_until_complete(frm.A.initialize(frm))
    loop.run_until_complete(asyncio.sleep(0.01))
    if os.path.exists(config.cache_file):
        pass
    else:
        gl.node_id, gl.node_ip = frm.A.show_status()
        gl.upload_size = frm.A.get_uploaded_size()

    try:
        loop.run_forever()
        # await asyncio.gather(self.A.initialize())
    except KeyboardInterrupt:
        frm.A.exit()
    finally:
        frm.A.exit()


if __name__ == '__main__':
    app = wx.App()
    frm = Myframe(None, "欢迎使用我们的P2P下载程序！")
    # frm.Show()
    loop = asyncio.get_event_loop()
    frm.loop = loop
    BACK = threading.Thread(target=launch, args=(frm,), daemon=True)
    BACK.start()
    app.MainLoop()
    BACK.join()
