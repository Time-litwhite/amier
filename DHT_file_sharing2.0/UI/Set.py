import wx
from kademlia.utils import config
from kademlia.API import API


class set(wx.Panel):
    def __init__(self, parent, A):
        wx.Panel.__init__(self, parent)

        self.DirInput = wx.DirDialog(self, u"请选择文件夹", style=wx.DD_DEFAULT_STYLE)
        self.API=A
        fgSizer1 = wx.FlexGridSizer(0, 1, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText1 = wx.StaticText(self, wx.ID_ANY, u"设置", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText1.Wrap(-1)

        self.m_staticText1.SetFont(
            wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "微软雅黑"))

        bSizer1.Add(self.m_staticText1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        fgSizer1.Add(bSizer1, 1, wx.EXPAND, 5)

        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText3 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(-1, 30), 0)
        self.m_staticText3.Wrap(-1)

        bSizer4.Add(self.m_staticText3, 0, wx.ALL, 5)

        fgSizer1.Add(bSizer4, 1, wx.EXPAND, 5)

        bSizer5 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, u"文件上传目录：", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)

        self.m_staticText4.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        bSizer5.Add(self.m_staticText4, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.Path1 = wx.TextCtrl(self, wx.ID_ANY, config.save_path, wx.DefaultPosition, wx.Size(250, -1), 0)
        bSizer5.Add(self.Path1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.m_staticText101 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(50, -1), 0)
        self.m_staticText101.Wrap(-1)

        bSizer5.Add(self.m_staticText101, 0, wx.ALL, 5)

        self.But1 = wx.Button(self, wx.ID_ANY, u"更改上传目录", wx.DefaultPosition, wx.DefaultSize, 0)
        self.But1.SetFont(
            wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        bSizer5.Add(self.But1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        fgSizer1.Add(bSizer5, 1, wx.EXPAND, 5)

        bSizer41 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText31 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(-1, 30), 0)
        self.m_staticText31.Wrap(-1)

        bSizer41.Add(self.m_staticText31, 0, wx.ALL, 5)

        fgSizer1.Add(bSizer41, 1, wx.EXPAND, 5)

        bSizer51 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText41 = wx.StaticText(self, wx.ID_ANY, u"文件下载目录：", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText41.Wrap(-1)

        self.m_staticText41.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        bSizer51.Add(self.m_staticText41, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.Path2 = wx.TextCtrl(self, wx.ID_ANY, config.download_path, wx.DefaultPosition, wx.Size(250, -1), 0)
        bSizer51.Add(self.Path2, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.m_staticText10 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(50, -1), 0)
        self.m_staticText10.Wrap(-1)

        bSizer51.Add(self.m_staticText10, 0, wx.ALL, 5)

        self.But2 = wx.Button(self, wx.ID_ANY, u"更改下载目录", wx.DefaultPosition, wx.DefaultSize, 0)
        self.But2.SetFont(
            wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))

        bSizer51.Add(self.But2, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        fgSizer1.Add(bSizer51, 1, wx.EXPAND, 5)

        self.SetSizer(fgSizer1)
        self.Layout()

        # Connect Events
        self.But1.Bind(wx.EVT_BUTTON, self.Change1)
        self.But2.Bind(wx.EVT_BUTTON, self.Change2)

    # class set(wx.Panel):
    #     def __init__(self, parent, A):
    #         wx.Panel.__init__(self, parent)
    #         bSizer1 = wx.FlexGridSizer(0, 1, 0, 0)
    #
    #         bSizer2 = wx.BoxSizer(wx.HORIZONTAL)
    #         bSizer3 = wx.BoxSizer(wx.HORIZONTAL)
    #
    #
    #         self.max_num = 0
    #         self.Hint1 = wx.StaticText(self, wx.ID_ANY, "根目录:  ", size=(50, 20))
    #         self.Dir = wx.StaticText(self, wx.ID_ANY, "请选择根目录", size=(400, 20))
    #         self.Setting1 = wx.Button(self, wx.ID_ANY, "选择", size=(35, 20))
    #         self.Hint2 = wx.StaticText(self, wx.ID_ANY, "最大连接数:  ", size=(75, 20))
    #         self.TextCrtl1 = wx.TextCtrl(self, wx.ID_ANY, "", size=(50, 20))
    #         self.Maxw = wx.StaticText(self, wx.ID_ANY, "", size=(100, 20))
    #         self.Setting2 = wx.Button(self, wx.ID_ANY, "选择", size=(35, 20))
    #         self.change = wx.Button(self, wx.ID_ANY, "修改", size=(35, 20))
    #         bSizer2.Add(self.Hint1)
    #         bSizer2.Add(self.Dir)
    #         bSizer2.Add(self.Setting1)
    #         bSizer3.Add(self.Hint2)
    #         bSizer3.Add(self.TextCrtl1)
    #         bSizer3.Add(self.Maxw)
    #         bSizer3.Add(self.Setting2)
    #         bSizer3.Add(self.change)
    #         self.Maxw.Hide()
    #         self.change.Hide()
    #
    #         self.m_text1 = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
    #         self.m_text2 = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
    #         self.m_text3 = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
    #         self.m_text4 = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
    #         self.m_text5 = wx.StaticText(self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
    #
    #         bSizer1.Add(self.m_text1, 1)
    #         bSizer1.Add(self.m_text2, 1)
    #         bSizer1.Add(self.m_text3, 1)
    #         bSizer1.Add(bSizer2, 1)
    #         bSizer1.Add(self.m_text4, 1)
    #         bSizer1.Add(self.m_text5, 1)
    #         bSizer1.Add(bSizer3, 1)
    #
    #         self.SetSizer(bSizer1)
    #         self.Layout()
    #
    #         self.Centre(wx.BOTH)
    #
    #         # Connect Events
    #         self.Setting1.Bind(wx.EVT_BUTTON, self.OnClick_Choice)
    #         self.Setting2.Bind(wx.EVT_BUTTON, self.OnCLick_Set)
    #         self.change.Bind(wx.EVT_BUTTON, self.OnClick_change)
    #
    #         # Virtual event handlers, override them in your derived class

    def Change1(self, event):
        if self.DirInput.ShowModal() == wx.ID_OK:
            path = self.DirInput.GetPath()
            self.Path1.SetLabel(path)
            self.API.modify_Configuration_save(path)

    def Change2(self, event):
        if self.DirInput.ShowModal() == wx.ID_OK:
            path = self.DirInput.GetPath()
            self.Path2.SetLabel(path)
            self.API.modify_Configuration_download(path)

    # 向API.modify_Configurantion传入save_path,max_connection和download_path
