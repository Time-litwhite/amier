import os
import pickle
import threading
import time
import pyperclip
import wx
import wx.xrc
from pubsub import pub
from kademlia.utils import config

Current_File_Pos = 70
Panel_List = []
FileNum = 0
FileSize = 0
To_API_Path = ''
Hash = None
API = None
Path_Hash_Mapping = {}


def size_format(size):
    if size < 1024:
        return '%i' % size + 'B'
    elif 1024 <= size < 1024 * 1024:
        return '%.1f' % float(size / 1024) + 'KB'
    elif 1024 * 1024 <= size < 1024 * 1024 * 1024:
        return '%.1f' % float(size / (1024 * 1024)) + 'MB'
    elif 1024 * 1024 * 1024 <= size < 1024 * 1024 * 1024 * 1024:
        return '%.1f' % float(size / (1024 * 1024 * 1024)) + 'GB'


class Gauge(wx.Gauge):
    def __init__(self, parent):
        wx.Gauge.__init__(self, parent, range=100, size=(500, 20), style=wx.GA_SMOOTH)

    # To API
    def progress(self, total_num, tasks, current_num, task):
        """
        将已完成任务task从tasks里移除，计算下载进度

        :param total_num: 分片总数
        :param tasks: 当前任务集合
        :param current_num: 当前已完成任务数目
        :param task: 当前任务
        :return:
        """
        tasks.discard(task)
        # current_num = total_num - len(tasks)
        current_num['n'] += 1
        self.SetRange(total_num)
        self.SetValue(current_num['n'])


class UpdateGauge(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.flag = 1
        self.start()

    def run(self):
        while self.flag == 1:
            pub.sendMessage("update")
            time.sleep(0.1)
            if self.flag != 1:
                return


class Notice_window(wx.Dialog):
    def __init__(self, parent, CID):
        wx.Dialog.__init__(self, parent, title='提示', pos=(1070, 175 + FileNum * 35), size=wx.Size(150, 80))
        if CID:
            Label = 'CID已复制到剪切板'
        else:
            Label = '文件上传成功！'
        Notice_TXT = wx.StaticText(self, label=Label)
        Box = wx.BoxSizer(wx.HORIZONTAL)
        Box.Add(Notice_TXT, 0, wx.ALL, 5)
        self.SetSizer(Box)
        self.Layout()


class Warning_window(wx.Dialog):
    def __init__(self, parent, type):
        wx.Dialog.__init__(self, parent, title='警告', pos=(650, 250), size=(250, 80))
        if type == 1:
            Label = '该文件已经发布，请勿重复发布！'
        if type == 2:
            Label = '该文件还未发布，请首先发布！'
        if type == 3:
            Label = '该文件已导入，请勿重复导入！'
        Warning_TXT = wx.StaticText(self, label=Label)
        Box = wx.BoxSizer(wx.HORIZONTAL)
        Box.Add(Warning_TXT, 0, wx.ALL, 5)
        self.SetSizer(Box)
        self.Layout()


class ListDialog(wx.Dialog):
    def __init__(self, parent, Hash=None, Panel=None, Map_path=None):
        wx.Dialog.__init__(self, parent, pos=(1070, 175 + FileNum * 35), size=wx.Size(110, 150))

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.Hash = Hash
        self.Panel = Panel
        self.Map_path = Map_path
        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"复制CID", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer1.Add(self.m_button1, 0, wx.ALL, 5)

        self.m_button3 = wx.Button(self, wx.ID_ANY, u"删除", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer1.Add(self.m_button3, 0, wx.ALL, 5)

        self.m_button4 = wx.Button(self, wx.ID_ANY, u'发布', wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer1.Add(self.m_button4, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.m_button1.Bind(wx.EVT_BUTTON, self.GetCID)
        self.m_button3.Bind(wx.EVT_BUTTON, self.Delete)
        self.m_button4.Bind(wx.EVT_BUTTON, self.UpLoad)

    def Delete(self, event):
        global Current_File_Pos
        global FileSize
        global Path_Hash_Mapping
        Current_File_Pos -= 35
        FileSize -= self.Panel.size
        self.sort()
        Path_Hash_Mapping.pop(self.Panel.Path)
        self.Destroy()
        self.Panel.Destroy()

    def sort(self):
        global FileNum
        global Panel_List
        j = 0
        for j in range(FileNum):
            if Panel_List[j] == self.Panel:
                del Panel_List[j]
                FileNum -= 1
                break
        for j in range(j, FileNum):
            Panel_List[j].SetPosition((Panel_List[j].GetPosition() - (0, 35)))

    def UpLoad(self, event):
        global To_API_Path
        global API
        global Path_Hash_Mapping
        To_API_Path = self.Panel.Path
        if To_API_Path in Path_Hash_Mapping.keys():
            Warning_window(self.Panel, 1).Show()
        else:
            file_hash = API._split_single_file(To_API_Path)
            Path_Hash_Mapping[To_API_Path] = file_hash
            API.upload(file_hash)
            # with open(self.Map_path, 'wb') as file:
            #     pickle.dump(Path_Hash_Mapping, file)
            Notice_window(self.Panel, None).Show()
        self.Destroy()

    # 获取CID#
    def GetCID(self, event):
        # self.CID=(API传来的CID)
        CID = Path_Hash_Mapping.get(self.Panel.Path)
        if CID:
            self.Panel.CID = CID
            Notice_window(self.Panel, CID).Show()
            pyperclip.copy(CID.hex())
        else:
            WAR = Warning_window(self.Panel, 2).Show()
            self.Panel.Layout()
        self.Destroy()  # 销毁自身


class NewFile(wx.Panel):
    def __init__(self, parent, FileName=None, Size=None, path=None, Map_path=None):
        wx.Panel.__init__(self, parent, pos=(-1, Current_File_Pos), size=wx.Size(800, 35))
        self.box = wx.BoxSizer(wx.HORIZONTAL)

        self.size = Size
        ####
        self.Path = path  # TO API
        self.CID = None  # From API
        ####

        self.FileName = wx.StaticText(self, wx.ID_ANY, FileName, wx.DefaultPosition, wx.Size(580, -1),
                                      style=wx.ALIGN_LEFT)
        self.box.Add(self.FileName, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.FileSize = wx.StaticText(self, wx.ID_ANY, size_format(self.size), wx.DefaultPosition, wx.Size(110, -1),
                                      0)
        self.FileSize.Wrap(-1)
        self.box.Add(self.FileSize, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.FileChose_List = wx.Button(self, wx.ID_ANY, u"·  ·  ·  ·", wx.DefaultPosition, wx.DefaultSize, 0)
        self.FileChose_List.Bind(wx.EVT_BUTTON,
                                 lambda e, Hash=self.FileName.Label, Panel=self, p=Map_path: self.FileChose_ListDialog(
                                     e, Hash,
                                     Panel, p))
        self.box.Add(self.FileChose_List, 0, wx.ALL, 5)

        self.SetSizer(self.box)

        Panel_List.append(self)
        self.Layout()

    def FileChose_ListDialog(self, event, Hash, Panel, p):
        ListDialog(self, Hash, Panel, p).Show()


class File(wx.Panel):

    def __init__(self, parent, A):
        wx.Panel.__init__(self, parent, size=wx.Size(720, 500))

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        # 变量
        global Current_File_Pos
        self.Current_File_Size = None
        self.Current_File_Name = None
        global API
        API = A
        self.Path_Hash_Mapping = {}
        self.Map_path = os.path.join(config.save_path, 'map.txt')
        self.Start = 0
        self.End = 0

        self.fgSizer2 = wx.FlexGridSizer(0, 1, 0, 0)
        self.fgSizer2.SetFlexibleDirection(wx.BOTH)
        self.fgSizer2.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.Hash = wx.TextCtrl(self, wx.ID_ANY, size=wx.Size(400, 25))
        bSizer2.Add(self.Hash, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.NoText = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(70, -1), 0)
        self.NoText.Wrap(-1)

        bSizer2.Add(self.NoText, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.Hash_search = wx.Button(self, wx.ID_ANY, u"搜索HASH", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.Hash_search, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.BlockSize = wx.StaticText(self, wx.ID_ANY, u"总大小:" + size_format(FileSize), wx.DefaultPosition,
                                       wx.Size(90, -1), style=wx.ALIGN_LEFT)
        self.BlockSize.Wrap(-1)
        bSizer2.Add(self.BlockSize, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.BlockSize_Show = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(20, -1), 0)
        self.BlockSize_Show.Wrap(-1)

        bSizer2.Add(self.BlockSize_Show, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.InputFile_Button = wx.Button(self, wx.ID_ANY, u"导入文件", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.InputFile_Button, 0, wx.ALL, 5)

        self.fgSizer2.Add(bSizer2, 1, wx.EXPAND, 5)

        bSizer11 = wx.BoxSizer(wx.HORIZONTAL)

        self.NameList = wx.Button(self, wx.ID_ANY, u"名称", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer11.Add(self.NameList, 0, wx.ALL, 5)

        self.Space = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(480, -1), 0)
        self.Space.Wrap(-1)

        bSizer11.Add(self.Space, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SizeList1 = wx.Button(self, wx.ID_ANY, u"大小", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer11.Add(self.SizeList1, 0, wx.ALL, 5)

        bbb = wx.BoxSizer(wx.VERTICAL)
        self.Space1 = wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(-1, 440), 0)

        bbb.Add(self.Space1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        Download = wx.BoxSizer(wx.HORIZONTAL)

        ##########################################################################################################################################

        # 下载进度
        self.Download_Gauge = Gauge(self)
        Download.Add(self.Download_Gauge, 0, wx.ALL, 5)
        self.Download_Progress = wx.StaticText(self, wx.ID_ANY, u"无下载任务", wx.DefaultPosition, wx.DefaultSize)
        Download.Add(self.Download_Progress, 0, wx.ALL, 5)
        ##########################################################################################################################################
        self.fgSizer2.Add(bSizer11, 1, wx.EXPAND, 5)
        self.fgSizer2.Add(bbb, 1, wx.EXPAND, 5)
        self.fgSizer2.Add(Download, 1, wx.EXPAND, 5)
        self.SetSizer(self.fgSizer2)
        self.Layout()

        self.Centre(wx.BOTH)
        pub.subscribe(self.Update_txt, "update")
        self.work = UpdateGauge()
        self.initial()
        # Connect Events
        self.InputFile_Button.Bind(wx.EVT_BUTTON, self.InputFile)  # 导入文件#
        self.Hash_search.Bind(wx.EVT_BUTTON, self.HashSearch)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.work.flag = 0

    # 运行时，从Map文件里初始化PHM字典。
    def initial(self):
        global Path_Hash_Mapping
        global FileSize
        if os.path.exists(self.Map_path):
            with open(self.Map_path, 'rb') as file:
                Path_Hash_Mapping = pickle.load(file)
            Path_List = list(Path_Hash_Mapping.keys())
            L = len(Path_List)
            for i in range(0, L):
                path = Path_List[i]
                FileSize += os.path.getsize(path)
                self.New_File(os.path.basename(path), os.path.getsize(path), path, self.Map_path)

    def InputFile(self, event):
        global FileSize
        FDialog = wx.FileDialog(self, message='选择文件', wildcard='*.*', style=wx.DEFAULT_DIALOG_STYLE)
        FDialog.ShowModal()
        if FDialog.GetPath():
            path = FDialog.GetPath()
            if path in Path_Hash_Mapping:
                Warning_window(self, 3).Show()
            else:
                self.Current_File_Size = os.path.getsize(path)
                FileSize += self.Current_File_Size
                self.New_File(FDialog.GetFilename(), self.Current_File_Size, path, self.Map_path)
        else:
            path = None

    def New_File(self, filename, size, path, P):
        NewFile(self, filename, size, path, P)
        global Current_File_Pos
        Current_File_Pos += 35
        global FileNum
        FileNum += 1
        self.Layout()

    def HashSearch(self, event):
        global Hash
        Hash = self.Hash.GetValue()
        API.download(Hash)
        self.Start = time.time_ns()/1000000000

    def Update_txt(self):
        current = self.Download_Gauge.GetValue()
        total = self.Download_Gauge.GetRange()
        self.BlockSize.SetLabel(u"块大小:" + size_format(FileSize))
        with open(self.Map_path, 'wb') as file:
            pickle.dump(Path_Hash_Mapping, file)
        progress = current / total * 100
        progress = round(progress, 2)

        if current == 0:
            return
        if current != total:  # 正在下载
            self.End = time.time_ns()/1000000000
            self.Download_Progress.SetLabel(f'下载进度:' + str(progress) + '%'+ '用时' + str(round(self.End - self.Start,2))+'s')
        else:
            self.Download_Progress.SetLabel(f'下载完成!' + '用时' + str(round(self.End - self.Start,2))+'s')
