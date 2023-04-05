# coding=gbk

import pygame
import random
import shutil
from tkinter import ttk
from tkinter.ttk import  Separator
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import askdirectory
import wave
import simpleaudio as sa
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import time
import os
from tkinter.filedialog import asksaveasfile

# 将当前工作目录切换到程序所在目录,否则在打包程序时会出现找不到图片的问题
os.chdir(os.path.dirname(__file__))
root=Tk()
root.title('SstnPlayer播放器')
root.geometry("450x750+192+108")
root.iconbitmap("my_logo.ico")
# 设置 SDL 环境变量，将 Pygame 的显示窗口设置为 Tkinter 的主窗口
os.environ['SDL_WINDOWID'] = str(root.winfo_id())
pygame.init()#pygame初始化
pygame.mixer.music.set_volume(1)  # 设置音量

playmode=IntVar() #播放模式
playmode.set(4) #默认播放模式：1单曲播放 2顺序播放 3随机播放 4选择播放 5列表循环播放
playstate=BooleanVar() #播放状态
playstate.set(0)   #1播放状态 0空闲状态
playlist=[]#播放列表
songname=StringVar()#用于显示歌曲路径+名称
songlenth=DoubleVar() #歌曲长度 浮点型变量
songlenth=0
songinfo=StringVar()#用于显示播放进度
randomindex=0 #列表框当前选择元组的下标
playtimeadd=0 #拖拽播放进度标尺时 所产生的进度增幅（它是一个时间差）
filesource=''

def addsong():#列表框添加歌曲
    with open('defpath.ini','r') as f:
        a = f.read()
        filetypes = [("音乐文件", "*.wav"),("音乐文件", "*.mp3"),("音乐文件", "*.flac"),("音乐文件", "*.ape")]
        files= askopenfilenames(title='请选择文件', filetypes=filetypes,initialdir=a)  # 打开当前程序工作目录,
        fsong=files[0]
        path=fsong[0:fsong.rfind('/')+1]

    with open('defpath.ini','w') as f:
        f.write(path)

    if len(files) != 0:
        for file in files:
            playlist.append(file)
            listbox.insert(END,file)
            listbox.bind('<Button-1>', getIndex)
            listbox.bind('<B1-Motion>', dragJob)
    listbox.select_set(0)
    return playlist


def delsong(): #从列表框删除歌曲
    indexs=listbox.curselection()  #用户在列表框上的选择，它返回一个元组，（即便单选也是返回一个元素的元组）
    for index in indexs[::-1]:
        #删除列表框项目要从后向前删除，如果正向删除，每删除一个项目时，它会扰乱列表其余部分的索引，你将不能得到正确的结果
        listbox.delete(index)
    playlist=[]
    for i in range(listbox.size()):
        playlist.append(listbox.get(i))
    # print(playlist)

def delall():#清空列表框
    for i in range(listbox.size())[::-1]:
        listbox.delete(i)
    playlist = []

def getIndex(event):  #绑定单击 列表框取得选择项目索引
    listbox.index=listbox.nearest(event.y)

def dragJob(event):  #绑定拖拽 列表框项目交换位置，同时更新列表：
    newIndex=listbox.nearest(event.y)
    if newIndex<listbox.index:
        x=listbox.get(newIndex)
        listbox.delete(newIndex)
        listbox.insert(newIndex+1,x)
        listbox.index=newIndex
    elif newIndex>listbox.index:
        x=listbox.get(newIndex)
        listbox.delete(newIndex)
        listbox.insert(newIndex-1,x)
        listbox.index=newIndex
    playlist=[]
    for i in range(listbox.size()):
        playlist.append(listbox.get(i))


def playtimeshow(): #播放进度显示
    global lentime
    if playstate.get()==1:
        if filesource[-3:]=='wav':
            song = WAVE(filesource)
            nowtime=time.time()
            lentime = nowtime - begintime
        elif filesource[-3:] == 'mp3' or filesource[-3:] == 'ape' or filesource[-4:] == 'flac':
            song = MP3(filesource)
            lentime = pygame.mixer.music.get_pos() / 1000
        playtime=lentime + playtimeadd
        songlenth=song.info.length
        h = '{0:02d}'.format(int(playtime / 3600))
        m = '{0:02d}'.format(int((playtime-3600*int(h)) / 60))
        s = '{0:02d}'.format(int((playtime-3600*int(h)) % 60))
        sh = '{0:02d}'.format(int(songlenth / 3600))
        sm = '{0:02d}'.format(int((songlenth-3600*int(sh)) / 60))
        ss = '{0:02d}'.format(int((songlenth-3600*int(sh)) % 60))
        songinfo.set("%s:%s:%s/%s:%s:%s" % (h, m, s, sh, sm, ss))
        songname.set(filesource)
        scale.config(from_=0,to=songlenth)
        scale.set(playtime)
        scale.bind('<ButtonRelease-1>', dragScaleJob)
    root.after(1000, playtimeshow)

def dragScaleJob(event):  #绑定拖拽 取得尺度条终值，松开鼠标时从终值开始播放：
    global playtimeadd
    if playstate.get()==1:
        if filesource[-3:]=='wav':
            from tkinter import messagebox
            messagebox.showinfo('MyMessagebox','wav文件不可快进和回退')
        elif filesource[-3:]=='mp3':
            scaleValue = scale.get()
            playtimeadd = scaleValue - lentime
            pygame.mixer.music.set_pos(scaleValue)


def single_play(): #播放
    global filesource,playtimeadd,play_obj,begintime
    playstate.set(1)   #设定播放状态标志
    playtimeadd=0 #进度增幅标尺 在启动时清零
    if playmode.get() == 1 : #单曲播放无randomindex，
        index=0   #播放选择元组中下标为0的歌曲（第一个），index=-1,则播放元组最后一只歌曲
    else:
        index = randomindex
    filesource = listbox.get(listbox.curselection()[index])
    print(filesource)
    sa.stop_all()
    if filesource[-3:] == 'wav':
        wave_read = wave.open(filesource, 'rb')
        wave_obj = sa.WaveObject.from_wave_read(wave_read)
        play_obj = wave_obj.play()
        begintime=time.time()
    elif filesource[-3:] == 'mp3' or filesource[-3:] == 'ape' or filesource[-4:] == 'flac':
        pygame.mixer.music.load(filesource)
        pygame.mixer.music.play()



def list_play(): #列表播放
    global randomindex,spconter
    if filesource[-3:] == 'mp3' or filesource[-3:] == 'ape' or filesource[-4:] == 'flac':
        if playmode.get() == 1 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            #单曲播放，要让list_play生效（playstate=1），必然调用一次single_play()，所以这里直接选择歌曲即可
            music_stop()
        elif playmode.get() == 2 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            #顺序播放
            selidex = listbox.curselection()[0]
            #由于列表框的选择模式是一直叠加，返回的是一个长度一直+1的元组，当向下迭代时，可以用下标[-1]来引用（最后一个）
            listbox.select_set(selidex,listbox.size())
            fileso = listbox.curselection()
            if randomindex < len(fileso) - 1:
                randomindex += 1
                single_play()
            else:
                music_stop()
                randomindex=0
        elif playmode.get() == 3 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            #随机播放
            conter=random.choice(range(len(playlist)-1)) #在列表的长度范围内创建一个随机整数conter
            print(str(eval(str(conter)))+playlist[conter])   #eval()16进制转10进制
            listbox.select_set(conter) #将conter做为索引加入列表框已选项目，它是一个元组，每loop一次，长度就会+1
            randomindex = listbox.curselection().index(conter)
            #将conter在listbox.curselection()的值中匹配，返回它在元组中的下标，做为全局变量提供给single_play()调用
            single_play()
        elif playmode.get() == 4 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            #选择播放
            fileso = listbox.curselection()
            if randomindex<len(fileso)-1:
                randomindex+=1
                single_play()
            else:
                music_stop()
                randomindex=0
        elif playmode.get() == 5 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            listbox.select_set(0,listbox.size())
            fileso = listbox.curselection()
            if randomindex < len(fileso) - 1:
                randomindex += 1
                single_play()
            else:
                randomindex = 0

    elif filesource[-3:] == 'wav':
        if playmode.get() == 1 and play_obj.is_playing() == False and playstate.get() == 1:
            #单曲播放，要让list_play生效（让playstate=1），必然调用一次single_play()，所以这里直接选择歌曲即可
            play_obj.stop()
        elif playmode.get() == 2 and play_obj.is_playing() == False and playstate.get() == 1:
            #顺序播放
            selidex = listbox.curselection()[0]
            #由于列表框的选择模式是一直叠加，返回的是一个长度一直+1的元组，当向下迭代时，可以用下标[-1]来引用（最后一个）
            listbox.select_set(selidex,listbox.size())
            fileso = listbox.curselection()
            if randomindex < len(fileso) - 1:
                randomindex += 1
                single_play()
            else:
                music_stop()
                randomindex=0
        elif playmode.get() == 3 and play_obj.is_playing() == False and playstate.get() == 1:
            #随机播放
            conter=random.choice(range(len(playlist)-1)) #在列表的长度范围内创建一个随机整数conter
            print(str(eval(str(conter)))+playlist[conter])   #eval()16进制转10进制
            listbox.select_set(conter) #将conter做为索引加入列表框已选项目，它是一个元组，每loop一次，长度就会+1
            randomindex = listbox.curselection().index(conter)
            #将conter在listbox.curselection()的值中匹配，返回它在元组中的下标，做为全局变量提供给single_play()调用
            single_play()
        elif playmode.get() == 4 and play_obj.is_playing() == False and playstate.get() == 1:
            #选择播放
            fileso = listbox.curselection()
            if randomindex<len(fileso)-1:
                randomindex+=1
                single_play()
            else:
                music_stop()
                randomindex=0
        elif playmode.get() == 5 and play_obj.is_playing() == False and playstate.get() == 1:
            listbox.select_set(0,listbox.size())
            fileso = listbox.curselection()
            if randomindex < len(fileso) - 1:
                randomindex += 1
                single_play()
            else:
                randomindex = 0
    root.after(3000, list_play)

def music_pause(): #暂停键
    pygame.mixer.music.pause()
    playstate.set(0)

def music_redo(): #暂停后继续键
    pygame.mixer.music.unpause()  # 继续播放
    playstate.set(1)

def music_stop(): #停止键
    if filesource[-3:] == 'wav':
        play_obj.stop()
    elif filesource[-3:] == 'mp3' or filesource[-3:] == 'ape' or filesource[-4:] == 'flac':
        pygame.mixer.music.stop()
    playstate.set(0)

def mp3ToWav():  #批量mp3转wav 原位置原名+扩展名wav
    filetypes = [("MP3文件", "*.mp3")]
    filenames = askopenfilenames(title='请选择文件', filetypes=filetypes,initialdir='./')  # 打开当前程序工作目录,
    if len(filenames) != 0:
        string_filename = ""
        for i in range(0, len(filenames)):
            mp3_to_wav(filenames[i])
            newname=filenames[i].replace('.mp3', '.wav')
            songinfo.set(filenames[i]+'==>'+newname+"转换完成")

def mp3_to_wav(filepath): #mp3转wav 原位置原名+扩展名wav
    song = AudioSegment.from_mp3(filepath)
    song.export(filepath.replace('.mp3','.wav'), format="wav")

def save_list():
    filetypes = [("列表文件", "*.lst")]
    filename=asksaveasfile(title='请输入列表文件名', defaultextension=".lst",
            filetypes=filetypes,initialdir='./')  # 打开当前程序工作目录,
    if filename =="":
        return           #如果不输入文件名，不向下执行
    print(filename)
    lists = [line + "\n" for line in playlist]
    with open(filename.name,"w") as f:
        f.writelines(lists)
    #这里先前用 with open(filename,"w") as f: 报错。
    # print(filenam) 显示 是< _io.TextIOWrapper name='E:/Python38/sstn/first_list.lst' mode='w' encoding='cp936'>
    #使用.name属性解决问题

def load_list():
    global playlist
    filetypes = [("列表文件", "*.lst")]
    filename = askopenfilename(title='请选择单个文件', filetypes=filetypes,
                               initialdir='./')  # 打开当前程序工作目录,
    if filename == "":
        return  # 如果不输入文件名，不向下执行
    delall()
    with open(filename, "r") as f:
        playlist=list(f)
        playlist = [line.strip("\n") for line in playlist]
    print(playlist)
    for i in range(len(playlist)):
        listbox.insert(END,playlist[i])
        listbox.bind('<Button-1>', getIndex)
        listbox.bind('<B1-Motion>', dragJob)
    listbox.select_set(0)
    playmode.set(1)
def lrc():
    lrc=Toplevel(root)

#顶面板 播放器按钮
pw=PanedWindow(root,orient=VERTICAL)
pw.pack(side=TOP,anchor=N,padx=5,pady=5,fill=Y)
pw.rowconfigure(0,weight=1)
pw.columnconfigure(0,weight=1)
imBt1 = PhotoImage(file="music1.png")
imBt2 = PhotoImage(file="music2.png")
imBt3 = PhotoImage(file="music3.png")
imBt4 = PhotoImage(file="music5.png")
btn2=Button(pw,text='pasue',image=imBt2,compound=TOP, width=60,command=music_pause)
btn3=Button(pw,text='redo',image=imBt3,compound=TOP, width=60,command=music_redo)
btn4=Button(pw,text='stop',image=imBt4,compound=TOP, width=60,command=music_stop)
btn1=Button(pw,text='play',image=imBt1,compound=TOP, width=60, command=single_play)
btn1.grid(row=0,column=0,padx=10,pady=10,sticky=W+E)
btn2.grid(row=0,column=1,padx=10,pady=10,sticky=W+E)
btn3.grid(row=0,column=2,padx=10,pady=10,sticky=W+E)
btn4.grid(row=0,column=3,padx=10,pady=10,sticky=W+E)
scale=Scale(pw,orient=HORIZONTAL,relief=GROOVE,showvalue=0)
scale.grid(row=1,column=0,columnspan=4,sticky=W+E)
sep=Separator(root)
sep.pack(fill=X,padx=5)
#播放模式选择面板
pw1=PanedWindow(root)
pw1.pack(side=TOP,anchor=N,padx=5,pady=5,fill=Y)
rb1=Radiobutton(pw1,variable=playmode, value=1, text="单曲播放")
rb2=Radiobutton(pw1,variable=playmode, value=2, text="顺序播放")
rb3=Radiobutton(pw1,variable=playmode, value=3, text="随机播放")
rb4=Radiobutton(pw1,variable=playmode, value=4, text="选择播放")
rb5=Radiobutton(pw1,variable=playmode, value=5, text="列表循环")
rb1.grid(row=0,column=0,padx=5)
rb2.grid(row=0,column=1,padx=5)
rb3.grid(row=0,column=2,padx=5)
rb4.grid(row=0,column=3,padx=5)
rb5.grid(row=0,column=4,padx=5)
#显示面板，用于显示歌曲信息
pwb=PanedWindow(root,orient=VERTICAL)
pwb.pack(expand=1,fill=BOTH)
scrollbar=Scrollbar(pwb)
scrollbar.pack(side=RIGHT,fill=Y,)
listbox = Listbox(pwb,yscrollcommand=scrollbar.set,selectmode=EXTENDED)
listbox.pack(side=LEFT,fill=BOTH,expand=1,padx=10)
scrollbar.config(command=listbox.yview)
#信息面板，各类操作信息显示
pwd=PanedWindow(root,orient=VERTICAL)
pwd.rowconfigure(0,weight=1)
pwd.columnconfigure(1,weight=1) #缩放第1列，来填充空白宽度空间，相当于pack的expand参数，
pwd.pack(expand=0,fill=BOTH)
lab1=Label(pwd,textvariable=songname,anchor=W,relief=FLAT)
lab2=Label(pwd,textvariable=songinfo,anchor=W,relief=FLAT)
lab3=Label(pwd,text='歌曲信息:',anchor=E,relief=FLAT)
lab4=Label(pwd,text='播放进度:',anchor=E,relief=FLAT)
lab1.grid(row=0,column=1,columnspan=2,ipadx=0,pady=5,sticky=W)
lab2.grid(row=1,column=1,columnspan=2,padx=0,pady=0,sticky=W)
lab3.grid(row=0,column=0,padx=5,sticky=W)
lab4.grid(row=1,column=0,padx=5,sticky=W)
#按钮面板
pwdd=PanedWindow(root,orient=VERTICAL)
pwdd.pack(expand=0,fill=BOTH,pady=5)
btn5=Button(pwdd,text='载入列表', command=load_list,bg="sky blue")
btn10=Button(pwdd,text='保存列表', command=save_list,bg="sky blue")
btn6=Button(pwdd,text='添加歌曲', command=addsong,bg="sky blue")
btn7=Button(pwdd,text='移除歌曲', command=delsong,bg="sky blue")
btn9=Button(pwdd,text='清空列表', command=delall, bg="sky blue")
btn8=Button(pwdd,text='格式转换', command=mp3ToWav,bg="sky blue")
btn5.grid(row=0,column=0,padx=5,ipadx=10,pady=10)
btn10.grid(row=0,column=1,padx=5,pady=10)
btn6.grid(row=0,column=2,padx=5,pady=10)
btn7.grid(row=0,column=3,padx=5,pady=10)
btn9.grid(row=0,column=4,padx=5,pady=10)
btn8.grid(row=0,column=5,padx=5,pady=10)

if __name__=="__main__":
    list_play()
    playtimeshow()


root.mainloop()

