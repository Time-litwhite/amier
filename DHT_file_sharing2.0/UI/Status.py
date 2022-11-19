import wx
import gl
from pubsub import pub
import threading
import time
import pyperclip


def size_format(size):
    if size < 1000:
        return '%i' % size + 'B'
    elif 1000 <= size < 1000000:
        return '%.1f' % float(size / 1000) + 'KB'
    elif 1000000 <= size < 1000000000:
        return '%.1f' % float(size / 1000000) + 'MB'
    elif 1000000000 <= size < 1000000000000:
        return '%.1f' % float(size / 1000000000) + 'GB'


class Notice_window(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, title='提示', pos=(700, 350), size=wx.Size(150, 85))
        Notice_TXT = wx.StaticText(self, label='IP地址已复制到剪切板')
        Box = wx.BoxSizer(wx.HORIZONTAL)
        Box.Add(Notice_TXT, 0, wx.ALL, 5)
        self.SetSizer(Box)
        self.Layout()


class UpdateThread_status(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.flag = 1
        self.start()

    def run(self):
        while self.flag ==1:
            pub.sendMessage("update")
            # if self.flag != 1:
            #     return
            time.sleep(1)


# 从API.show_status获取自身的IP，ID，以及从get_uoloaded_size获取托管文件大小
class Link(wx.Panel):
    def __init__(self, parent, A):
        wx.Panel.__init__(self, parent)
        bSizer1 = wx.BoxSizer(wx.VERTICAL)
        self.API = A
        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"已连接到P2P下载器", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)
        self.m_staticText1.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "宋体"))
        bSizer5.Add(self.m_staticText1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        bSizer2.Add(bSizer5, 1, wx.EXPAND, 5)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"已托管 0B 文件", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer6.Add(self.m_button1, 0, wx.ALL, 5)

        bSizer2.Add(bSizer6, 1, wx.EXPAND, 5)

        bSizer7 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText3 = wx.StaticText(self, wx.ID_ANY, u"节点ID", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)

        bSizer7.Add(self.m_staticText3, 0, wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, u"            ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)

        bSizer7.Add(self.m_staticText4, 0, wx.ALL, 5)

        self.m_staticText5 = wx.StaticText(self, wx.ID_ANY, gl.node_id, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText5.Wrap(-1)

        bSizer7.Add(self.m_staticText5, 0, wx.ALL, 5)

        bSizer2.Add(bSizer7, 1, wx.EXPAND, 5)

        bSizer9 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText9 = wx.StaticText(self, wx.ID_ANY, u"UI版本", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText9.Wrap(-1)

        bSizer9.Add(self.m_staticText9, 0, wx.ALL, 5)

        self.m_staticText10 = wx.StaticText(self, wx.ID_ANY, u"            ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText10.Wrap(-1)

        bSizer9.Add(self.m_staticText10, 0, wx.ALL, 5)

        self.m_staticText11 = wx.StaticText(self, wx.ID_ANY, u"v1.0beta版", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText11.Wrap(-1)

        bSizer9.Add(self.m_staticText11, 0, wx.ALL, 5)

        bSizer2.Add(bSizer9, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer2, 1, wx.EXPAND, 5)

        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        bSizer10 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText12 = wx.StaticText(self, wx.ID_ANY, u"ip地址", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText12.Wrap(-1)

        bSizer10.Add(self.m_staticText12, 0, wx.ALL, 5)

        self.IP_Button = wx.Button(self, wx.ID_ANY, gl.node_ip, wx.DefaultPosition, size=(400, -1))

        bSizer10.Add(self.IP_Button, 0, wx.ALL, 5)

        bSizer3.Add(bSizer10, 1, wx.EXPAND, 5)

        bSizer11 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText15 = wx.StaticText(self, wx.ID_ANY, u"API", wx.DefaultPosition, size=(50, 25), style=0)
        self.m_staticText15.Wrap(-1)

        bSizer11.Add(self.m_staticText15, 0, wx.ALL, 5)

        self.m_staticText16 = wx.StaticText(self, wx.ID_ANY, u"                 ", wx.DefaultPosition, size=(10, 25),
                                            style=0)
        self.m_staticText16.Wrap(-1)

        bSizer11.Add(self.m_staticText16, 0, wx.ALL, 5)

        self.flag = 1
        self.m_staticText17 = wx.StaticText(self, wx.ID_ANY, u"/ip4/127.0.0.1/tcp/5001", wx.DefaultPosition,
                                            size=(150, 25), style=0)
        self.m_staticText17.Wrap(-1)
        self.m_textctrl1 = wx.TextCtrl(self, wx.ID_ANY, u"/ip4/127.0.0.1/tcp/5001", wx.DefaultPosition,
                                       size=(150, 25), style=0)

        bSizer11.Add(self.m_staticText17, 0, wx.ALL)
        bSizer11.Add(self.m_textctrl1, 0, wx.ALL)
        self.m_textctrl1.Hide()

        self.m_button3 = wx.Button(self, wx.ID_ANY, u"编辑")
        bSizer11.Add(self.m_button3, 0, wx.ALL, 5)

        bSizer3.Add(bSizer11, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer3, 1, wx.EXPAND, 5)

        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        bSizer1.Add(bSizer4, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.Centre(wx.BOTH)
        self.work = UpdateThread_status()
        pub.subscribe(self.UpdateLabel, "update")
        # Connect Events
        # self.m_button1.Bind(wx.EVT_BUTTON, self.ONClick_file)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.IP_Button.Bind(wx.EVT_BUTTON, self.OnClick_IP)
        self.m_button3.Bind(wx.EVT_BUTTON, self.Onclick_settings)

    def OnClose(self, event):
        self.work.flag = 0

    def OnClick_IP(self, event):
        pyperclip.copy(self.IP_Button.Label)
        Notice_window(self).Show()

    def Onclick_settings(self, event):
        if self.flag:
            self.m_staticText17.Hide()
            self.m_textctrl1.Show()
            self.flag = 0
            self.Layout()
        else:
            self.m_staticText17.Show()
            self.m_textctrl1.Hide()
            self.flag = 1
            self.m_staticText17.SetLabel(self.m_textctrl1.Value)
            self.Layout()

    def UpdateLabel(self):
        time.sleep(0.1)
        gl.node_id, gl.node_ip = self.API.show_status()
        gl.upload_size = self.API.get_uploaded_size()
        str1 = "已托管" + size_format(gl.upload_size) + "文件"
        self.m_button1.SetLabel(str1)
        self.m_staticText5.SetLabel(gl.node_id)
        self.IP_Button.SetLabel(gl.node_ip)
