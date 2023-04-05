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

# ����ǰ����Ŀ¼�л�����������Ŀ¼,�����ڴ������ʱ������Ҳ���ͼƬ������
os.chdir(os.path.dirname(__file__))
root=Tk()
root.title('SstnPlayer������')
root.geometry("450x750+192+108")
root.iconbitmap("my_logo.ico")
# ���� SDL ������������ Pygame ����ʾ��������Ϊ Tkinter ��������
os.environ['SDL_WINDOWID'] = str(root.winfo_id())
pygame.init()#pygame��ʼ��
pygame.mixer.music.set_volume(1)  # ��������

playmode=IntVar() #����ģʽ
playmode.set(4) #Ĭ�ϲ���ģʽ��1�������� 2˳�򲥷� 3������� 4ѡ�񲥷� 5�б�ѭ������
playstate=BooleanVar() #����״̬
playstate.set(0)   #1����״̬ 0����״̬
playlist=[]#�����б�
songname=StringVar()#������ʾ����·��+����
songlenth=DoubleVar() #�������� �����ͱ���
songlenth=0
songinfo=StringVar()#������ʾ���Ž���
randomindex=0 #�б��ǰѡ��Ԫ����±�
playtimeadd=0 #��ק���Ž��ȱ��ʱ �������Ľ�������������һ��ʱ��
filesource=''

def addsong():#�б����Ӹ���
    with open('defpath.ini','r') as f:
        a = f.read()
        filetypes = [("�����ļ�", "*.wav"),("�����ļ�", "*.mp3"),("�����ļ�", "*.flac"),("�����ļ�", "*.ape")]
        files= askopenfilenames(title='��ѡ���ļ�', filetypes=filetypes,initialdir=a)  # �򿪵�ǰ������Ŀ¼,
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


def delsong(): #���б��ɾ������
    indexs=listbox.curselection()  #�û����б���ϵ�ѡ��������һ��Ԫ�飬�����㵥ѡҲ�Ƿ���һ��Ԫ�ص�Ԫ�飩
    for index in indexs[::-1]:
        #ɾ���б����ĿҪ�Ӻ���ǰɾ�����������ɾ����ÿɾ��һ����Ŀʱ�����������б����ಿ�ֵ��������㽫���ܵõ���ȷ�Ľ��
        listbox.delete(index)
    playlist=[]
    for i in range(listbox.size()):
        playlist.append(listbox.get(i))
    # print(playlist)

def delall():#����б��
    for i in range(listbox.size())[::-1]:
        listbox.delete(i)
    playlist = []

def getIndex(event):  #�󶨵��� �б��ȡ��ѡ����Ŀ����
    listbox.index=listbox.nearest(event.y)

def dragJob(event):  #����ק �б����Ŀ����λ�ã�ͬʱ�����б�
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


def playtimeshow(): #���Ž�����ʾ
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

def dragScaleJob(event):  #����ק ȡ�ó߶�����ֵ���ɿ����ʱ����ֵ��ʼ���ţ�
    global playtimeadd
    if playstate.get()==1:
        if filesource[-3:]=='wav':
            from tkinter import messagebox
            messagebox.showinfo('MyMessagebox','wav�ļ����ɿ���ͻ���')
        elif filesource[-3:]=='mp3':
            scaleValue = scale.get()
            playtimeadd = scaleValue - lentime
            pygame.mixer.music.set_pos(scaleValue)


def single_play(): #����
    global filesource,playtimeadd,play_obj,begintime
    playstate.set(1)   #�趨����״̬��־
    playtimeadd=0 #����������� ������ʱ����
    if playmode.get() == 1 : #����������randomindex��
        index=0   #����ѡ��Ԫ�����±�Ϊ0�ĸ�������һ������index=-1,�򲥷�Ԫ�����һֻ����
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



def list_play(): #�б���
    global randomindex,spconter
    if filesource[-3:] == 'mp3' or filesource[-3:] == 'ape' or filesource[-4:] == 'flac':
        if playmode.get() == 1 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            #�������ţ�Ҫ��list_play��Ч��playstate=1������Ȼ����һ��single_play()����������ֱ��ѡ���������
            music_stop()
        elif playmode.get() == 2 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            #˳�򲥷�
            selidex = listbox.curselection()[0]
            #�����б���ѡ��ģʽ��һֱ���ӣ����ص���һ������һֱ+1��Ԫ�飬�����µ���ʱ���������±�[-1]�����ã����һ����
            listbox.select_set(selidex,listbox.size())
            fileso = listbox.curselection()
            if randomindex < len(fileso) - 1:
                randomindex += 1
                single_play()
            else:
                music_stop()
                randomindex=0
        elif playmode.get() == 3 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            #�������
            conter=random.choice(range(len(playlist)-1)) #���б�ĳ��ȷ�Χ�ڴ���һ���������conter
            print(str(eval(str(conter)))+playlist[conter])   #eval()16����ת10����
            listbox.select_set(conter) #��conter��Ϊ���������б����ѡ��Ŀ������һ��Ԫ�飬ÿloopһ�Σ����Ⱦͻ�+1
            randomindex = listbox.curselection().index(conter)
            #��conter��listbox.curselection()��ֵ��ƥ�䣬��������Ԫ���е��±꣬��Ϊȫ�ֱ����ṩ��single_play()����
            single_play()
        elif playmode.get() == 4 and pygame.mixer.music.get_busy() == False and playstate.get() == 1:
            #ѡ�񲥷�
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
            #�������ţ�Ҫ��list_play��Ч����playstate=1������Ȼ����һ��single_play()����������ֱ��ѡ���������
            play_obj.stop()
        elif playmode.get() == 2 and play_obj.is_playing() == False and playstate.get() == 1:
            #˳�򲥷�
            selidex = listbox.curselection()[0]
            #�����б���ѡ��ģʽ��һֱ���ӣ����ص���һ������һֱ+1��Ԫ�飬�����µ���ʱ���������±�[-1]�����ã����һ����
            listbox.select_set(selidex,listbox.size())
            fileso = listbox.curselection()
            if randomindex < len(fileso) - 1:
                randomindex += 1
                single_play()
            else:
                music_stop()
                randomindex=0
        elif playmode.get() == 3 and play_obj.is_playing() == False and playstate.get() == 1:
            #�������
            conter=random.choice(range(len(playlist)-1)) #���б�ĳ��ȷ�Χ�ڴ���һ���������conter
            print(str(eval(str(conter)))+playlist[conter])   #eval()16����ת10����
            listbox.select_set(conter) #��conter��Ϊ���������б����ѡ��Ŀ������һ��Ԫ�飬ÿloopһ�Σ����Ⱦͻ�+1
            randomindex = listbox.curselection().index(conter)
            #��conter��listbox.curselection()��ֵ��ƥ�䣬��������Ԫ���е��±꣬��Ϊȫ�ֱ����ṩ��single_play()����
            single_play()
        elif playmode.get() == 4 and play_obj.is_playing() == False and playstate.get() == 1:
            #ѡ�񲥷�
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

def music_pause(): #��ͣ��
    pygame.mixer.music.pause()
    playstate.set(0)

def music_redo(): #��ͣ�������
    pygame.mixer.music.unpause()  # ��������
    playstate.set(1)

def music_stop(): #ֹͣ��
    if filesource[-3:] == 'wav':
        play_obj.stop()
    elif filesource[-3:] == 'mp3' or filesource[-3:] == 'ape' or filesource[-4:] == 'flac':
        pygame.mixer.music.stop()
    playstate.set(0)

def mp3ToWav():  #����mp3תwav ԭλ��ԭ��+��չ��wav
    filetypes = [("MP3�ļ�", "*.mp3")]
    filenames = askopenfilenames(title='��ѡ���ļ�', filetypes=filetypes,initialdir='./')  # �򿪵�ǰ������Ŀ¼,
    if len(filenames) != 0:
        string_filename = ""
        for i in range(0, len(filenames)):
            mp3_to_wav(filenames[i])
            newname=filenames[i].replace('.mp3', '.wav')
            songinfo.set(filenames[i]+'==>'+newname+"ת�����")

def mp3_to_wav(filepath): #mp3תwav ԭλ��ԭ��+��չ��wav
    song = AudioSegment.from_mp3(filepath)
    song.export(filepath.replace('.mp3','.wav'), format="wav")

def save_list():
    filetypes = [("�б��ļ�", "*.lst")]
    filename=asksaveasfile(title='�������б��ļ���', defaultextension=".lst",
            filetypes=filetypes,initialdir='./')  # �򿪵�ǰ������Ŀ¼,
    if filename =="":
        return           #����������ļ�����������ִ��
    print(filename)
    lists = [line + "\n" for line in playlist]
    with open(filename.name,"w") as f:
        f.writelines(lists)
    #������ǰ�� with open(filename,"w") as f: ����
    # print(filenam) ��ʾ ��< _io.TextIOWrapper name='E:/Python38/sstn/first_list.lst' mode='w' encoding='cp936'>
    #ʹ��.name���Խ������

def load_list():
    global playlist
    filetypes = [("�б��ļ�", "*.lst")]
    filename = askopenfilename(title='��ѡ�񵥸��ļ�', filetypes=filetypes,
                               initialdir='./')  # �򿪵�ǰ������Ŀ¼,
    if filename == "":
        return  # ����������ļ�����������ִ��
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

#����� ��������ť
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
#����ģʽѡ�����
pw1=PanedWindow(root)
pw1.pack(side=TOP,anchor=N,padx=5,pady=5,fill=Y)
rb1=Radiobutton(pw1,variable=playmode, value=1, text="��������")
rb2=Radiobutton(pw1,variable=playmode, value=2, text="˳�򲥷�")
rb3=Radiobutton(pw1,variable=playmode, value=3, text="�������")
rb4=Radiobutton(pw1,variable=playmode, value=4, text="ѡ�񲥷�")
rb5=Radiobutton(pw1,variable=playmode, value=5, text="�б�ѭ��")
rb1.grid(row=0,column=0,padx=5)
rb2.grid(row=0,column=1,padx=5)
rb3.grid(row=0,column=2,padx=5)
rb4.grid(row=0,column=3,padx=5)
rb5.grid(row=0,column=4,padx=5)
#��ʾ��壬������ʾ������Ϣ
pwb=PanedWindow(root,orient=VERTICAL)
pwb.pack(expand=1,fill=BOTH)
scrollbar=Scrollbar(pwb)
scrollbar.pack(side=RIGHT,fill=Y,)
listbox = Listbox(pwb,yscrollcommand=scrollbar.set,selectmode=EXTENDED)
listbox.pack(side=LEFT,fill=BOTH,expand=1,padx=10)
scrollbar.config(command=listbox.yview)
#��Ϣ��壬���������Ϣ��ʾ
pwd=PanedWindow(root,orient=VERTICAL)
pwd.rowconfigure(0,weight=1)
pwd.columnconfigure(1,weight=1) #���ŵ�1�У������հ׿�ȿռ䣬�൱��pack��expand������
pwd.pack(expand=0,fill=BOTH)
lab1=Label(pwd,textvariable=songname,anchor=W,relief=FLAT)
lab2=Label(pwd,textvariable=songinfo,anchor=W,relief=FLAT)
lab3=Label(pwd,text='������Ϣ:',anchor=E,relief=FLAT)
lab4=Label(pwd,text='���Ž���:',anchor=E,relief=FLAT)
lab1.grid(row=0,column=1,columnspan=2,ipadx=0,pady=5,sticky=W)
lab2.grid(row=1,column=1,columnspan=2,padx=0,pady=0,sticky=W)
lab3.grid(row=0,column=0,padx=5,sticky=W)
lab4.grid(row=1,column=0,padx=5,sticky=W)
#��ť���
pwdd=PanedWindow(root,orient=VERTICAL)
pwdd.pack(expand=0,fill=BOTH,pady=5)
btn5=Button(pwdd,text='�����б�', command=load_list,bg="sky blue")
btn10=Button(pwdd,text='�����б�', command=save_list,bg="sky blue")
btn6=Button(pwdd,text='��Ӹ���', command=addsong,bg="sky blue")
btn7=Button(pwdd,text='�Ƴ�����', command=delsong,bg="sky blue")
btn9=Button(pwdd,text='����б�', command=delall, bg="sky blue")
btn8=Button(pwdd,text='��ʽת��', command=mp3ToWav,bg="sky blue")
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

