#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import random
import mutagen
from PyQt5.QtGui import QPalette, QColor, QIcon, QFont, QPixmap
from PyQt5.QtCore import QUrl, QDirIterator, Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, \
QPushButton, QFileDialog, QAction, QHBoxLayout, QVBoxLayout, QSlider, \
QToolTip, QLabel, QListWidget, QListWidgetItem, QProgressBar, QComboBox
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer() # 播放器
        self.playlist = QMediaPlaylist() # 播放列表
        self.title = '音乐播放器'
        self.volumeHint = QLabel('音量: 99%')
        self.mInfo = {
            'cover': './default_cover.jpg', 
            'music': '', 
            'singer': '',
            'duration': 0
        }
        self.aboutWin = AboutWindow()
        self.cover = QLabel()
        self.listWid = QListWidget()

        # 设置主窗口位置
        self.left = 200
        self.top = 100
        self.width = 500
        self.height = 430

        self.font = QFont('SansSerif', 10.5)
        self.color = 1  # 0 - 黑色界面, 1 - 白色界面
        self.userAction = 0  # 0 - 停止中, 1 - 播放中 2 - 暂停中
        self.initUI()

    def initUI(self):
        # 添加文件菜单
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False) # 不使用本地菜单栏以获得全平台统一的效果
        filemenu = menubar.addMenu('文件')
        windowmenu = menubar.addMenu('窗口')

        fileAct = QAction('打开文件', self)
        folderAct = QAction('打开文件夹', self)
        themeAct = QAction('切换[亮/暗]主题', self)
        aboutAct = QAction('关于', self)

        fileAct.setShortcut('Ctrl+O')
        folderAct.setShortcut('Ctrl+D')
        themeAct.setShortcut('Ctrl+T')
        aboutAct.setShortcut('Ctrl+H')

        filemenu.addAction(fileAct)
        filemenu.addAction(folderAct)
        windowmenu.addAction(themeAct)
        windowmenu.addAction(aboutAct)

        fileAct.triggered.connect(self.openFile)
        folderAct.triggered.connect(self.addFiles)
        themeAct.triggered.connect(self.toggleColors)
        aboutAct.triggered.connect(self.viewAbout)
        self.listWid.itemDoubleClicked.connect(self.quickplayhandler)

        self.listWid.setFont(self.font)
        self.playlist.setPlaybackMode(2)
        self.setLayout()
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint) # 禁用窗口最大化按钮
        self.setFont(self.font)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.toggleColors()
        self.show()

    def setLayout(self):
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # 添加音量控制
        volumeslider = QSlider(Qt.Horizontal, self)
        volumeslider.setFocusPolicy(Qt.NoFocus)
        volumeslider.valueChanged[int].connect(self.changeVolume)
        volumeslider.setValue(100)

        # 添加歌曲播放控制
        playBtn = QPushButton('播放')  # 播放
        pauseBtn = QPushButton('暂停')  # 暂停
        stopBtn = QPushButton('清空列表')  # 停止
        prevBtn = QPushButton('上一首') # 上一首
        playback = QComboBox() # 回放模式
        nextBtn = QPushButton('下一首') # 下一首

        playback.addItem('      单曲播放')
        playback.addItem('      单曲循环')
        playback.addItem('      列表播放')
        playback.addItem('      列表循环')
        playback.addItem('      列表随机')

        playback.setCurrentIndex(2)

        # 添加封面
        jpg = QPixmap(self.mInfo['cover']).scaled(300, 300)
        self.cover.setPixmap(jpg)

        # 添加布局
        Area = QVBoxLayout()  # centralWidget
        controls = QHBoxLayout()
        showLayout = QHBoxLayout()
        playlistCtrlLayout = QHBoxLayout()

        # 歌曲播放控制布局
        controls.addWidget(playBtn)
        controls.addWidget(pauseBtn)
        controls.addWidget(stopBtn)

        # 播放列表控制布局
        playlistCtrlLayout.addWidget(prevBtn)
        playlistCtrlLayout.addWidget(playback)
        playlistCtrlLayout.addWidget(nextBtn)

        # 显示布局
        showLayout.addWidget(self.cover)
        showLayout.addWidget(self.listWid)

        # 竖直排列
        Area.addStretch(1)
        Area.addLayout(showLayout)
        Area.addWidget(self.volumeHint)
        Area.addWidget(volumeslider)
        Area.addLayout(controls)
        Area.addLayout(playlistCtrlLayout)
        wid.setLayout(Area)

        # 事件绑定
        playBtn.clicked.connect(self.playhandler)
        pauseBtn.clicked.connect(self.pausehandler)
        playback.currentIndexChanged.connect(self.playbackhandler)
        stopBtn.clicked.connect(self.stophandler)

        prevBtn.clicked.connect(self.prevSong)
        nextBtn.clicked.connect(self.nextSong)

        self.statusBar().showMessage('文件-打开文件(夹)-选择-开始播放')
        self.playlist.currentMediaChanged.connect(self.songChanged)

    def openFile(self):
        print("点击了文件按钮")
        song = QFileDialog.getOpenFileName(self, "打开音频", "github-lkxed", "音频文件 (*.mp3 *.ogg *.wav *.m4a)")

        if song[0] != '':
            url = QUrl.fromLocalFile(song[0])
            if self.playlist.mediaCount() == 0:
                self.playlist.addMedia(QMediaContent(url))
                self.player.setPlaylist(self.playlist)
                self.player.play()
                self.userAction = 1
                self.listWid.addItem(song[0].split('/')[-1].split('.')[0])
                print(self.playlist.mediaCount())
            else:
                self.playlist.addMedia(QMediaContent(url))
                print(self.playlist.mediaCount())

    def addFiles(self):
        print("点击了文件夹按钮")
        if self.playlist.mediaCount() != 0:
            self.folderIterator()
            print(self.playlist.mediaCount())
        else:
            self.folderIterator()
            self.player.setPlaylist(self.playlist)
            self.player.playlist().setCurrentIndex(0)
            self.player.play()
            print(self.playlist.mediaCount())
            self.userAction = 1
    
    def folderIterator(self):
        folderChosen = QFileDialog.getExistingDirectory(self, '打开音频文件夹', '.')
        if folderChosen != None:
            it = QDirIterator(folderChosen)
            it.next()
            while it.hasNext():
                if it.fileInfo().isDir() == False and it.filePath() != '.':
                    fInfo = it.fileInfo()
                    print(it.filePath(), fInfo.suffix())
                    if fInfo.suffix() in ('mp3', 'ogg', 'wav', 'm4a'):
                        print('added file', fInfo.fileName())
                        self.listWid.addItem(fInfo.fileName())
                        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                it.next()
            if it.fileInfo().isDir() == False and it.filePath() != '.':
                fInfo = it.fileInfo()
                print(it.filePath(), fInfo.suffix())
                if fInfo.suffix() in ('mp3', 'ogg', 'wav', 'm4a'):
                    print('added file', fInfo.fileName())
                    self.listWid.addItem(fInfo.fileName())
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))

            # 设置ListItem高度
            for x in range(self.listWid.count()):
                self.listWid.item(x).setSizeHint(QSize(100, 30))

    # 处理双击播放事件
    def quickplayhandler(self, item):
        # 若播放列表没有音频了就跳出打开文件对话框
        if self.playlist.mediaCount() == 0:
            self.openFile()
        # 若播放列表不为空则播放
        elif self.playlist.mediaCount() != 0:
            index = self.listWid.currentRow()
            self.player.playlist().setCurrentIndex(index)
            self.player.play()
            self.userAction = 1

    # 处理按钮播放事件
    def playhandler(self):
        if self.userAction == 2:
            self.player.play()
        elif self.userAction == 0:
            # 若播放列表没有音频了就跳出打开文件对话框
            if self.playlist.mediaCount() == 0:
                self.openFile()
            # 若播放列表不为空则播放
            elif self.playlist.mediaCount() != 0:
                index = self.listWid.currentRow()
                self.player.playlist().setCurrentIndex(index)
                self.player.play()
                self.userAction = 1
        else:
            self.statusBar().showMessage('已经在播放中!')

    # 处理暂停事件
    def pausehandler(self):
        self.userAction = 2
        self.player.pause()

    # 处理清空列表事件
    def stophandler(self):
        self.userAction = 0
        self.player.stop()
        self.playlist.clear()
        self.listWid.clear()
        self.mInfo['cover'] = 'default_cover.jpg'
        jpg = QPixmap(self.mInfo['cover']).scaled(300, 300)
        self.cover.setPixmap(jpg)
        print("Playlist cleared!")
        self.statusBar().showMessage("列表已清空")

    def changeVolume(self, value):
        text = '音量: ' + str(value) + '%'
        self.volumeHint.setText(text)
        self.player.setVolume(value)

    # 上一首事件
    def prevSong(self):
        if self.playlist.currentIndex() == 0:
            self.playlist.setCurrentIndex(self.playlist.mediaCount()-1)
        else:
            self.player.playlist().previous()
    
    # 随机播放事件
    def playbackhandler(self, index):
        self.playlist.setPlaybackMode(index)
        print(self.playlist.playbackMode())

    # 下一首事件
    def nextSong(self):
        if self.playlist.mediaCount() == self.playlist.currentIndex()+1:
            self.playlist.setCurrentIndex(0)
        else:
            self.player.playlist().next()
    
    # 音频切换事件
    def songChanged(self, media):
        if not media.isNull():
            url = media.canonicalUrl()
            self.showInfo(url)
            self.statusBar().showMessage(url.fileName())
            index = self.player.playlist().currentIndex()
            self.listWid.setCurrentRow(index)

    def showInfo(self, url):
        filepath = url.path()[1:]
        filename = url.fileName()[:-4]
        print(filename)
        if filepath[-3:] == 'm4a':
            file = mutagen.MP4(filepath)
            try:
                img = file.tags['covr'][0]
                self.mInfo['cover'] = './cover/'+filename+'.jpg'
                if not os.path.exists('./cover'):
                    os.mkdir('./cover')
                if not os.path.exists(self.mInfo['cover']):
                    with open(self.mInfo['cover'], 'wb') as f:
                        f.write(img)
            except:
                print('找不到封面')
                self.mInfo['cover'] = './default_cover.jpg'

        elif filepath[-3:] == 'mp3':
            file = mutagen.File(filepath)
            try:
                img = file.tags['APIC:'].data
                self.mInfo['cover'] = './cover/'+filename+'.jpg'
                if not os.path.exists('./cover'):
                    os.mkdir('./cover')
                if not os.path.exists(self.mInfo['cover']):
                    with open(self.mInfo['cover'], 'wb') as f:
                        f.write(img)
            except:
                print('找不到封面')
                self.mInfo['cover'] = './default_cover.jpg'
        else:
            print('音频文件不支持提取封面')
            self.mInfo['cover'] = './default_cover.jpg'

        jpg = QPixmap(self.mInfo['cover']).scaled(300, 300)
        self.cover.setPixmap(jpg)


    # 主题切换事件
    def toggleColors(self):

        app.setStyle("Fusion")
        palette = QPalette()

        # 明亮主题
        if self.color == 0:
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(235, 101, 54))
            palette.setColor(QPalette.Highlight, QColor(235, 101, 54))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = 1

        # 黑暗主题
        elif self.color == 1:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, QColor(240, 240, 240))
            palette.setColor(QPalette.AlternateBase, Qt.white)
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, Qt.white)
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(66, 155, 248))
            palette.setColor(QPalette.Highlight, QColor(66, 155, 248))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            self.color = 0

    def viewAbout(self):
        self.aboutWin.show()

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('关于')
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint) # 禁用窗口最大化按钮
        layout = QVBoxLayout()
        layout.addWidget(QLabel('作者: lkxed'))
        siteLink = QLabel('网站: <a href="https://www.lkxed.cn">https://www.lkxed.cn</a>')
        siteLink.setOpenExternalLinks(True)
        layout.addWidget(siteLink)
        srcLink = QLabel('源码: 在 <a href="https://github.com/lkxed/MusicPlayer">GitHub</a> 上查看')
        srcLink.setOpenExternalLinks(True)
        layout.addWidget(srcLink)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setLayout(layout)
        self.resize(200, 100)
        self.setFixedSize(200, 100)
        self.move(300, 200)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
