import wx
import wx.xrc
from pubsub import pub
import threading
import time


class UpdateThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.flag = 1
        self.start()

    def run(self):
        while self.flag == 1:
            pub.sendMessage("update")
            # if self.flag!=1:
            #     return
            time.sleep(2.5)


class NewNod(wx.Panel):
    def __init__(self, parent, node_id, node_ip, Current_Node_Pos):
        wx.Panel.__init__(self, parent, wx.ID_ANY, (-1, Current_Node_Pos), (800, 50))
        self.Node_Box = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText7 = wx.StaticText(self, id=wx.ID_ANY, label=node_id, pos=wx.DefaultPosition,
                                           size=(350,-1), style=wx.ALIGN_CENTER)
        self.m_staticText7.Wrap(-1)

        self.Node_Box.Add(self.m_staticText7, 0, wx.ALL, 5)

        self.m_staticText9 = wx.StaticText(self, id=wx.ID_ANY, label=node_ip, pos=wx.DefaultPosition,
                                           size=(350,-1), style=wx.ALIGN_CENTER)
        self.m_staticText9.Wrap(-1)

        self.Node_Box.Add(self.m_staticText9, 0, wx.ALL, 5)
        self.SetSizer(self.Node_Box)
        self.Layout()


class node(wx.Panel):

    def __init__(self, parent, A=None):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(800, 500))

        # 表示输入IP,TO API.add_connection as ip
        self.Input_IP = ""
        # 表示节点id
        self.node_id = ""
        # 表示节点ip
        self.node_ip = ""
        # 表示节点列表
        self.node_list = []
        # 表示最大节点数量
        self.node_num = 30
        # 已显示节点列表
        self.Node_List = []
        # 已显示节点数目
        self.NodeNum = 0
        #
        self.API = A
        # 当前位置
        self.Current_Node_Pos = 90
        # 步长
        self.Step = 25

        self.fgSizer1 = wx.FlexGridSizer(0, 1, 0, 0)
        self.fgSizer1.SetFlexibleDirection(wx.BOTH)
        self.fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        Search_Box = wx.BoxSizer(wx.HORIZONTAL)
        self.m_textctrl1 = wx.TextCtrl(self, wx.ID_ANY, u"", wx.DefaultPosition, size=(200, 30), style=0)

        Search_Box.Add(self.m_textctrl1, 0, wx.ALL, 5)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"建立连接", wx.DefaultPosition, size=(100, 30), style=0)

        Search_Box.Add(self.m_button1, 0, wx.ALL, 5)

        self.RefreshButton = wx.Button(self, wx.ID_ANY, u"刷新节点", size=(100, 30))

        Search_Box.Add(self.RefreshButton, 0, wx.ALL, 5)
        self.fgSizer1.Add(Search_Box, 1, wx.EXPAND, 5)

        Title_Box = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"节点ID", wx.DefaultPosition, (350,-1), style=wx.ALIGN_CENTER)
        self.m_staticText1.Wrap(-1)

        self.m_staticText1.SetFont(
            wx.Font(28, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "宋体"))

        Title_Box.Add(self.m_staticText1, 0, wx.ALL, 5)

        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"IP地址", wx.DefaultPosition, (350,-1), style=wx.ALIGN_CENTER)
        self.m_staticText2.Wrap(-1)

        self.m_staticText2.SetFont(
            wx.Font(28, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "宋体"))

        Title_Box.Add(self.m_staticText2, 0, wx.ALL, 5)


        self.RefreshButton.Bind(wx.EVT_BUTTON, self.Refresh_Node)

        self.fgSizer1.Add(Title_Box, 1, wx.EXPAND, 5)

        Node_Box = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText7 = wx.StaticText(self, wx.ID_ANY, u"（节点ID）", wx.DefaultPosition, (350,-1), style=wx.ALIGN_CENTER)
        self.m_staticText7.Wrap(-1)

        Node_Box.Add(self.m_staticText7, 0, wx.ALL, 5)

        self.m_staticText9 = wx.StaticText(self, wx.ID_ANY, u"(IP地址）", wx.DefaultPosition, (350,-1), style=wx.ALIGN_CENTER)
        self.m_staticText9.Wrap(-1)

        Node_Box.Add(self.m_staticText9, 0, wx.ALL, 5)

        self.fgSizer1.Add(Node_Box, 1, wx.EXPAND, 5)

        self.SetSizer(self.fgSizer1)
        self.Layout()
        self.work = UpdateThread()
        self.m_button1.Bind(wx.EVT_BUTTON, self.Get_IP)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        pub.subscribe(self.UpdateNode, "update")

    def OnClose(self, event):
        self.work.flag = 0

    def Refresh_nodelist(self):
        self.node_list = self.API.show_peers()

    def Get_IP(self, event):
        self.Input_IP = self.m_textctrl1.GetValue()
        if self.Input_IP:
            self.API.add_connection(self.Input_IP)
        self.m_textctrl1.SetValue("")
        self.Refresh_nodelist()

    def Refresh_Node(self, event):
        if len(self.Node_List):
            self.Delete_Node_All()
        for i in range(0, len(self.node_list)):
            self.AddNode()
        self.Layout()

    def AddNode(self):
        self.node_id = self.node_list[len(self.Node_List)][0]
        self.node_ip = self.node_list[len(self.Node_List)][1]
        self.Node_List.append(NewNod(self, self.node_id, self.node_ip, self.Current_Node_Pos))
        self.Current_Node_Pos += self.Step
        self.Layout()

    def Delete_Node_All(self):
        for i in range(0, len(self.Node_List)):
            self.Node_List[i].Destroy()
        for i in range(0, len(self.Node_List)):
            del self.Node_List[0]
        self.Current_Node_Pos = 90
        self.Layout()

    def UpdateNode(self):
        "刷新node_list"
        self.Refresh_nodelist()
