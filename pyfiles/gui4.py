import os,sys
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import cv2 as cv
import shutil
import mediapipe as mp
import numpy as np
import pandas as pd
import dask.dataframe as dd
import copy
from PIL import Image, ImageDraw, ImageFont
import glob
import re
import collections
#import decimal

# 参照ボタンのイベント
# button3クリック時の処理
def button3_clicked():
    fTyp = [("","jpg"),("","png")]
    dir_path = file2.get() #ID参照

    dirname = os.getcwd()
    data_path=os.path.join(dirname,'../Data/')
    #Data/IDを出力
    iDir = os.path.join(data_path,dir_path)
    #face_pic
    iDir2 = os.path.join(iDir,'face_pic')

    filepath = filedialog.askopenfilename(filetypes = fTyp, initialdir = iDir2)
    file3.set(filepath)#face_77.jpg

def button4_clicked(): #[距離計算開始]
    dir_path = file2.get()
    dirname = os.getcwd()

    #最も良い顔画像
    s=file3.get()
    #文字列から数字取得
    resultnum = re.findall(r"\d+", s)
    num=int(resultnum[-1])

    print('Best:',num)
    #part.csv読み込み

    part_path=os.path.join(dirname,'pyfiles/part.csv')

    #face.csv読み込み

    data_path=os.path.join(dirname,'../Data/')
    #Data/IDを出力
    iDir = os.path.join(data_path,dir_path)


    fa=pd.read_csv(os.path.join(iDir, dir_path+'_face.csv'),header=None,index_col=[0,1,2])#index=[フレーム数，1, ポイント]
    fan=fa.loc[num]#numフレーム目
    #199顎-4鼻=基準距離

    disv=fan.loc[1,199]-fan.loc[1,4]

    dis=np.linalg.norm(disv)

    #hand.csv読み込み
    ha=pd.read_csv(os.path.join(iDir, dir_path+'_hand.csv'),header=None,index_col=[0,1,2])
    ha=ha.iloc[:,:3].dropna()

    hb=copy.copy(ha)
    hb=hb.iloc[:,:0]
    hb['face_point']=999
    hb['face_part']='None'
    hb['distance_pixel']=9999

    pa=pd.read_csv(part_path,header=None)


    #距離の小さいものを排除
    #全フレーム
    fr=int(len(ha)/42)
    print(fr)
    for i in range(fr):

        #両手
        for j in range(2):
            #全て0でない場合
            if(np.any(ha.loc[i+1,j]!=0)):
                #print(i+1,j)
                #顎鼻>2掌
                print(np.linalg.norm(ha.loc[i+1,j,0]-ha.loc[i+1,j,9])< 0.5*dis)
                if (np.linalg.norm(ha.loc[i+1,j,0]-ha.loc[i+1,j,9])< 0.5*dis):
                    #0扱い
                    ha.loc[i+1,j]=0

    #左右入れ替えアルゴリズム
    kx=fan.loc[1,4][3]

    #左右入れ替えアルゴリズム
    for i in range(fr):

        lx=ha.loc[i+1,0,0][3]
        rx=ha.loc[i+1,1,0][3]
        #両手検知ver.
        if (lx!=0) and (rx!=0 ):
            if lx > rx :
                p0=np.array(ha.loc[i+1,0])
                p1=np.array(ha.loc[i+1,1])
                ha.loc[i+1,1]=p0
                ha.loc[i+1,0]=p1
        #左手検知ver.
        elif (lx!=0) & (rx==0 ):
            if lx > kx :
                p0=np.array(ha.loc[i+1,0])
                p1=np.array(ha.loc[i+1,1])
                ha.loc[i+1,1]=p0
                ha.loc[i+1,0]=p1
        #右手検知ver.
        elif (lx==0) & (rx!=0 ):
            if kx > rx :
                p0=np.array(ha.loc[i+1,0])
                p1=np.array(ha.loc[i+1,1])
                ha.loc[i+1,1]=p0
                ha.loc[i+1,0]=p1


    #修正したものを改めてhands.csvとして作成
    df=pd.DataFrame(ha)
    df.to_csv(os.path.join(iDir,dir_path+'_hand.csv'), header=None)
    #距離計算+追加情報付与
    #全フレーム
    fr=int(len(ha)/42)
    #keyframe
    for i in range(fr):

        #両手
        for j in range(2):
            #全て0でない場合
            if(np.any(ha.loc[i+1,j]!=0)):
                print(i+1,j)
                for k in range(21):
                    num2=rdo_var.get()

                    dlis=np.sqrt((((fa.loc[num]-ha.loc[1+i,j,k]).iloc[:,:2+num2])**2).sum(axis=1))

                    hb.loc[1+i,j,k]=[dlis.argmin(),pa.iloc[dlis.argmin(),0],dlis.min()]


    df=pd.DataFrame(hb)
    df.to_csv(os.path.join(iDir,dir_path+'_distance.csv'),header=None)

    return messagebox.showinfo('計算終了', '完了')

def button45_clicked():#[位置情報付与]
    dir_path = file2.get()
    dirname = os.getcwd()

    data_path=os.path.join(dirname,'../Data/')
    #Data/IDを出力
    iDir = os.path.join(data_path,dir_path)



    basename4 = 'pic'
    base_path4 = os.path.join(iDir, basename4)

    #動画のFPS情報
    l2 = os.path.join(iDir, dir_path+'.mov')
    cap = cv.VideoCapture(l2)
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    frr = cap.get(cv.CAP_PROP_FPS)
    #分割したものを動画化
    fourcc = cv.VideoWriter_fourcc('m','p','4', 'v')
    video_f  = cv.VideoWriter(os.path.join(iDir,dir_path+'_Video.mp4'), fourcc, frr, (w, h))

    l = glob.glob(os.path.join(base_path4,'*'))
    l.sort()
    real_m=len([name for name in os.listdir(base_path4) if os.path.isfile(os.path.join(base_path4, name))])
    print(real_m)

    #distance.csv読み込み
    da=pd.read_csv(os.path.join(iDir,dir_path+'_distance.csv'),header=None,index_col=[0,1,2])

    #最短ポイント情報
    #hp=['手首']+['親指']*4+['人差指']*4+['中指']*4+['薬指']*4+['小指']*4
    #hl=[]
    fl=[]
    #hr=[]
    fr=[]
    th=10

    #最短ポイント情報
    for i in range(real_m):
        #左手
        #am=da.loc[i+1,0][5].argmin()
        #minp=da.loc[i+1,0,am][4]

        #閾値による分類

        p=da.loc[i+1,0][4][da.loc[i+1,0][5]<th]
        if len(p)==0:
            #hl.append('無し')
            fl.append('無し')
        else:
            c = collections.Counter(p)
            fp=c.most_common()[0][0]
            fl.append(fp)
        #if minp=="None":
         #   hl.append('無し')
          #  fl.append('無し')
        #else:
         #   hl.append(hp[am])
          #  fl.append(minp)

        #右手
        #amr=da.loc[i+1,1][5].argmin()
        #minpr=da.loc[i+1,1,amr][4]

        #if minpr=="None":
          #  hr.append('無し')
           # fr.append('無し')
        #else:
         #   hr.append(hp[amr])
          #  fr.append(minpr)
        p=da.loc[i+1,1][4][da.loc[i+1,1][5]<th]
        if len(p)==0:
            #hr.append('無し')
            fr.append('無し')
        else:
            c = collections.Counter(p)
            fp=c.most_common()[0][0]
            fr.append(fp)



    #画像に挿入
    for i in range(real_m):
        print(i)
        text0 ='左手:'+fl[i]
        text1 ='右手:'+fr[i]
        #秒数
        text2 = '{:.03f}'.format(i/frr)+'s'     # 画像に追加する文字列を指定
        img = Image.open(l[i]) # 入力ファイルを指定
        imagesize = img.size        # img.size[0]は幅、img.size[1]は高さを表す
        draw = ImageDraw.Draw(img)  # ImageDrawオブジェクトを作成

        font = ImageFont.truetype("Arial Unicode.ttf", 32)  # フォントを指定、64はサイズでピクセル単位
        size = font.getsize(text2)

        # 画像右下に'Sampleと表示' #FFFは文字色（白）
        #左上→右手情報
        draw.text((size[0], size[1]), text1, font=font, fill='#FFF',stroke_width=4,stroke_fill='black')
        draw.text((imagesize[0]-size[0]*3.5, size[1]), text0, font=font, fill='#FFF',stroke_width=4,stroke_fill='black')
        draw.text((imagesize[0] - size[0], imagesize[1] - size[1]), text2, font=font, fill='#FFF',stroke_width=4,stroke_fill='black')

        # ファイルを保存
        img.save(l[i], quality=100, optimize=True)
        video_f.write(cv.imread(l[i]))

    video_f.release()

    return messagebox.showinfo('計算終了', '完了')



def button5_clicked():
    file1_entry.delete(0, END)
    file2_entry.delete(0, END)
    file3_entry.delete(0, END)






if __name__ == '__main__':
    # rootの作成
    root = Tk()
    root.title('Mediapipe Tool')
    root.resizable(False, False)

    #####Frame1の作成
    frame1 = ttk.Frame(root, padding=10)
    frame1.grid()

    # 参照ボタンの作成
    #button1 = ttk.Button(root, text=u'動画を探す', command=button1_clicked)
    #button1.grid(row=0, column=3)

    # ラベルの作成
    # 「ファイル」ラベルの作成
    #s = StringVar()
    #s.set('動画ファイルPath>>')
    #label1 = ttk.Label(frame1, textvariable=s)
    #label1.grid(row=0, column=0)

    # 参照ファイルパス表示ラベルの作成
    #file1 = StringVar()
    #file1_entry = ttk.Entry(frame1, textvariable=file1, width=50)
    #file1_entry.grid(row=0, column=2)

    ####ID入力欄
    # Frame2の作成
    frame2 = ttk.Frame(root, padding=(0,5))
    frame2.grid(row=1)
    # ラベルの作成
    # 「ファイル」ラベルの作成
    s1 = StringVar()
    s1.set('ID>>')
    label2 = ttk.Label(frame2, textvariable=s1)
    label2.grid(row=1, column=0)

    # 参照ファイルパス表示ラベルの作成
    file2 = StringVar()
    file2_entry = ttk.Entry(frame2, textvariable=file2, width=10)
    file2_entry.grid(row=1, column=2)



    ####Frame2の作成
    frame3 = ttk.Frame(root, padding=(0,5))
    frame3.grid(row=2)

    # 骨格抽出ボタンの作成
    #button2 = ttk.Button(frame3, text='骨格抽出開始', command=button2_clicked)
    #button2.pack(side=LEFT)

    ####顔のフレーム
    frame4 = ttk.Frame(root, padding=(5,5))
    frame4.grid(row=3)

    # 顔ボタンの作成
    button3 = ttk.Button(root, text=u'顔フレーム検索', command=button3_clicked)
    button3.grid(row=3, column=3)

    # ラベルの作成
    # 「ファイル」ラベルの作成
    s2 = StringVar()
    s2.set('画像ファイルPath>>')
    label3 = ttk.Label(frame4, textvariable=s2)
    label3.grid(row=3, column=0)

    # 参照ファイルパス表示ラベルの作成
    file3 = StringVar()
    file3_entry = ttk.Entry(frame4, textvariable=file3, width=50)
    file3_entry.grid(row=3, column=2)


    #####ラジオボタンフレーム
    frame5 = ttk.Frame(root, padding=(10,5))
    frame5.grid(row=4,column=0)

    # ラジオボタンの状態
    rdo_var = IntVar()

    rb1 = ttk.Radiobutton(frame5,text=u'XY',value=0,variable=rdo_var)
    rb1.pack(side=LEFT)

    # Radiobutton 2
    rb2 = ttk.Radiobutton(frame5,text=u'XYZ',value=1,variable=rdo_var)
    rb2.grid(row=4, column=3)##怪しい
    rb2.pack(side=RIGHT)
    #####フレーム
    frame6 = ttk.Frame(root, padding=(0,5))
    frame6.grid(row=5)
    # ボタンの作成
    button4 = ttk.Button(frame6, text='距離計算開始', command=button4_clicked)
    button4.pack(side=RIGHT)

    ###新規フレーム
    #####フレーム
    frame65 = ttk.Frame(root, padding=(0,5))
    frame65.grid(row=6)
    # ボタンの作成
    button45 = ttk.Button(frame65, text='位置情報付与', command=button45_clicked)
    button45.pack(side=RIGHT)




    #####フレーム
    frame7 = ttk.Frame(root, padding=(0,5))
    frame7.grid(row=9)


    # Cancelボタンの作成
    button5 = ttk.Button(frame7, text='リセット', command=button5_clicked)
    button5.pack(side=LEFT)


    # Cancelボタンの作成
    button6 = ttk.Button(frame7, text='終了', command=quit)
    button6.pack(side=LEFT)

    root.mainloop()
