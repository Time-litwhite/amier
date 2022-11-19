import wx



class status(wx.Panel):
    def __init__(self, parent, A):
        wx.Panel.__init__(self, parent)
        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        # self.m_bitmap1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(
        #     u"C:\\Users\\21101\\PycharmProjects\\软件工程\\ui\\notybook\\right1.png", wx.BITMAP_TYPE_ANY),
        #                                  wx.DefaultPosition, wx.Size(100, 100), 0)
        # bSizer6.Add(self.m_bitmap1, 0, wx.ALIGN_BOTTOM, 5)

        self.m_staticText18 = wx.StaticText(self, wx.ID_ANY, u"\n\n已连接到P2P下载器", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_staticText18.Wrap(-1)

        self.m_staticText18.SetFont(
            wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "宋体"))

        bSizer6.Add(self.m_staticText18, 0, wx.ALL, 5)

        bSizer2.Add(bSizer6, 1, wx.EXPAND, 5)

        bSizer7 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText3 = wx.StaticText(self, wx.ID_ANY,
                                           u"            欢迎来到未来的互联网！您现在已经成为分布式网络上不可或缺的一部分。",
                                           wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)

        self.m_staticText3.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "宋体"))

        bSizer7.Add(self.m_staticText3, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        bSizer2.Add(bSizer7, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer2, 1, wx.EXPAND, 5)

        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, u"这个应用中，您可以...", wx.DefaultPosition, wx.DefaultSize,
                                           0)
        self.m_staticText4.Wrap(-1)

        self.m_staticText4.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "宋体"))

        bSizer4.Add(self.m_staticText4, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.m_staticText5 = wx.StaticText(self, wx.ID_ANY,
                                           u"检查您的节点状态，这里包含了您所有连接到的其他节点、您的存储\n和带宽使用状态等等",
                                           wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText5.Wrap(-1)

        bSizer4.Add(self.m_staticText5, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.m_staticText6 = wx.StaticText(self, wx.ID_ANY,
                                           u"您在IPFS库中查看和管理文件，包含使用拖拽来导入、固定、和快速\n分享和下载选项",
                                           wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText6.Wrap(-1)

        bSizer4.Add(self.m_staticText6, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.m_staticText7 = wx.StaticText(self, wx.ID_ANY,
                                           u"      访问\"Merkle Forest\"和一些示例数据集，并探索IPLD——这是一种支持\n      IPFS工作的数据模型",
                                           wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText7.Wrap(-1)

        bSizer4.Add(self.m_staticText7, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.m_staticText8 = wx.StaticText(self, wx.ID_ANY,
                                           u"  查看谁连接到了您的节点，并根据他们的IP地址在世界地图上显示定位",
                                           wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText8.Wrap(-1)

        bSizer4.Add(self.m_staticText8, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.m_staticText9 = wx.StaticText(self, wx.ID_ANY, u"      查看和编辑您的节点设定 —— 不需要通过命令行终端",
                                           wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText9.Wrap(-1)

        bSizer4.Add(self.m_staticText9, 0, wx.ALL, 5)

        bSizer3.Add(bSizer4, 1, wx.EXPAND, 5)

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText11 = wx.StaticText(self, wx.ID_ANY, u"  P2P下载是什么？", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText11.Wrap(-1)

        self.m_staticText11.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "宋体"))

        bSizer5.Add(self.m_staticText11, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.m_staticText12 = wx.StaticText(self, wx.ID_ANY,
                                            u"    融合了Kademlia、BitTorrent、Git等理念的一种超媒体分发协议",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText12.Wrap(-1)

        bSizer5.Add(self.m_staticText12, 0, wx.ALL, 5)

        self.m_staticText13 = wx.StaticText(self, wx.ID_ANY,
                                            u"    避免了中心节点失效，无审查和管控的完全去中心化的点到点传输网络",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText13.Wrap(-1)

        bSizer5.Add(self.m_staticText13, 0, wx.ALL, 5)

        self.m_staticText14 = wx.StaticText(self, wx.ID_ANY,
                                            u"    驶入互联网的明天——传统浏览器可以通过访问地址如https://ipfs.io\n    等的公共IPFS网关，或者安装IPFS 伴侣扩展来访问储存在IPFS网络中\n    的文件",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText14.Wrap(-1)

        bSizer5.Add(self.m_staticText14, 0, wx.ALL, 5)

        self.m_staticText15 = wx.StaticText(self, wx.ID_ANY,
                                            u"    依托强大的开源社区为后盾，为构建完整分布式应用和服务的一个开发\n    者工具集",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText15.Wrap(-1)

        bSizer5.Add(self.m_staticText15, 0, wx.ALL, 5)

        self.m_staticText16 = wx.StaticText(self, wx.ID_ANY,
                                            u"    下一代内容分发网络CDN——只需要在本地节点添加文件就可以使得\n    全球都可以通过缓存友好的内容哈希地址和类BitTorrent网络带宽分发\n    来获得文件",
                                            wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText16.Wrap(-1)
        bSizer5.Add(self.m_staticText16, 0, wx.ALL, 5)

        bSizer3.Add(bSizer5, 1, wx.EXPAND, 5)

        bSizer1.Add(bSizer3, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Centre(wx.BOTH)



