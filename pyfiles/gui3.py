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
# button1クリック時の処理
def button1_clicked():
    fTyp = [("","mov"),("","mp4")]
    #iDir = os.path.abspath(os.path.dirname(__file__))
    #iDir = '.'
    filepath = filedialog.askopenfilename(filetypes = fTyp)
    file1.set(filepath)


# button2クリック時の処理
def button2_clicked():
    res=messagebox.askokcancel('準備完了', u'動画ファイル:\n' + file1.get()+u'\nID:\n' + file2.get()+'\n\nOKを押すと処理が始まります.\nOKを押したら，完了するまで暫くお待ちください.')

    if res == False:
        return 0

    video_path = file1.get()
    cap = cv.VideoCapture(video_path)

    if not cap.isOpened():
        return messagebox.showinfo('処理中断', '動画が読み込めませんでした')
    dir_path = file2.get()
    basename = 'frame'
    basename2 = 'hand'
    basename3 = 'hand_face'
    basename4 = 'split'
    #dirpathフォルダ
    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)
    base_path2 = os.path.join(dir_path, basename2)
    base_path3 = os.path.join(dir_path, basename3)
    base_path4 = os.path.join(dir_path, basename4)
    
    #frameフォルダ
    #os.makedirs(base_path, exist_ok=True)
    base_path1 = os.path.join(base_path, basename)
    #handフォルダ
    #os.makedirs(base_path2, exist_ok=True)
    base_path2 = os.path.join(base_path2, basename2)
    #faceフォルダ
    os.makedirs(base_path3, exist_ok=True)
    base_path3 = os.path.join(base_path3, basename3)
    #splitフォルダ
    os.makedirs(base_path4, exist_ok=True)
    base_path4 = os.path.join(base_path4, basename4)
    

    #元動画をコピー
    shutil.copy(video_path, dir_path)

    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    digit = len(str(int(cap.get(cv.CAP_PROP_FRAME_COUNT))))
    maisu = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    frr = cap.get(cv.CAP_PROP_FPS)
    print('Frame数',cap.get(cv.CAP_PROP_FRAME_COUNT))

    print('FPS',cap.get(cv.CAP_PROP_FPS))
    print('秒数',cap.get(cv.CAP_PROP_FRAME_COUNT) / cap.get(cv.CAP_PROP_FPS))

    #分割したものを動画化
    fourcc = cv.VideoWriter_fourcc('m','p','4', 'v')
    #video  = cv.VideoWriter(os.path.join(dir_path,'handVideo.mp4'), fourcc, frr, (w, h))
    video_f  = cv.VideoWriter(os.path.join(dir_path,'hand_faceVideo.mp4'), fourcc, frr, (w, h))

    #手の座標を収めるarray
    #array=np.array([[[0.0]*21]*6]*maisu)
    array=np.array([[0.0]*6]*maisu*42)
    #顔の座標を収めるarray *()注意)データ量を考慮して今回は計算しない
    array_f=np.array([[0.0]*6]*maisu*468)

    #インデックス整理
    a0=[]
    a1=[]
    a2=[]
    b0=[]
    b2=[]

    for i in range(maisu):
        a0+=[i+1]*42
        b0+=[i+1]*468
        a1+=[0]*21+[1]*21
        a2+=list(range(21))+list(range(21))
        b2+=list(range(468))
    array[:,0]=a0
    array[:,1]=a1
    array[:,2]=a2
    array_f[:,0]=b0
    array_f[:,1]=1
    array_f[:,2]=b2


    n = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(n,'/',maisu)
            #元画像保存
            cv.imwrite('{}_{}.{}'.format(base_path4, str(n).zfill(digit), 'jpg'),frame) # 保存


            #元動画のフレーム分割&書き出し
            #cv.imwrite('{}_{}.{}'.format(base_path1, str(n).zfill(digit), 'jpg'), frame)

            #mpインスタンス
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing_styles = mp.solutions.drawing_styles
            mp_hands = mp.solutions.hands
            mp_drawing = mp.solutions.drawing_utils
            mp_face_mesh = mp.solutions.face_mesh # MLソリューションの顔メッシュインスタンス

            hands = mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.7)

            face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                min_detection_confidence=0.5)

            drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
            image = frame



            results = hands.process(cv.flip(cv.cvtColor(image, cv.COLOR_BGR2RGB), 1))
            results_f = face_mesh.process(cv.flip(cv.cvtColor(image, cv.COLOR_BGR2RGB), 1))

            annotated_image = cv.flip(image.copy(), 1) # 描画用の画像をコピーしておく
            #annotated_image =  np.zeros((w,h,3),np.uint8)*255

            ###検知できた手の数で場合わけ
            #検知できなかった場合
            if type(results.multi_handedness)==type(None):

                array[n*42:(n+1)*42,3]=0
                array[n*42:(n+1)*42,4]=0
                array[n*42:(n+1)*42,5]=0
                #画像の保存
                #cv.imwrite('{}_{}.{}'.format(base_path2, str(n).zfill(digit), 'jpg'),cv.flip(annotated_image, 1)) # 保存
                #video.write(cv.flip(annotated_image, 1))
            elif len(results.multi_handedness)==1:

                for hand_landmarks in results.multi_hand_landmarks:
                     mp_drawing.draw_landmarks(
                      annotated_image,
                      hand_landmarks,
                      mp_hands.HAND_CONNECTIONS,
                      mp_drawing_styles.get_default_hand_landmarks_style(),
                      mp_drawing_styles.get_default_hand_connections_style())

                    #mp_drawing.draw_landmarks(
                    #    annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)# 特徴点の描画
                #画像の保存
                #cv.imwrite('{}_{}.{}'.format(base_path2, str(n).zfill(digit), 'jpg'),cv.flip(annotated_image, 1))  # 保存
                #video.write(cv.flip(annotated_image, 1))

                #左手のみ検知
                if "Left" in str(results.multi_handedness[0].classification):

                    for j in range(21):
                        array[42*n+j,3]=results.multi_hand_landmarks[0].landmark[j].x*w
                        array[42*n+j,4]=(1-results.multi_hand_landmarks[0].landmark[j].y)*h
                        array[42*n+j,5]=results.multi_hand_landmarks[0].landmark[j].z*w
                        array[42*n+21+j,3]=0
                        array[42*n+21+j,4]=0
                        array[42*n+21+j,5]=0


                #右手のみ検知
                elif "Right" in str(results.multi_handedness[0].classification) :

                    for j in range(21):
                        array[42*n+j,3]=0
                        array[42*n+j,4]=0
                        array[42*n+j,5]=0
                        array[42*n+21+j,3]=results.multi_hand_landmarks[0].landmark[j].x*w
                        array[42*n+21+j,4]=(1-results.multi_hand_landmarks[0].landmark[j].y)*h
                        array[42*n+21+j,5]=results.multi_hand_landmarks[0].landmark[j].z*w

                    #array[i,1]=float(results.multi_hand_landmarks[0].landmark)

            #両手の検知
            elif len(results.multi_handedness)==2:

                for hand_landmarks in results.multi_hand_landmarks:
                     mp_drawing.draw_landmarks(
                      annotated_image,
                      hand_landmarks,
                      mp_hands.HAND_CONNECTIONS,
                      mp_drawing_styles.get_default_hand_landmarks_style(),
                      mp_drawing_styles.get_default_hand_connections_style())

                    #mp_drawing.draw_landmarks(
                    #    annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)# 特徴点の描画
                #画像の保存
                #cv.imwrite('{}_{}.{}'.format(base_path2, str(n).zfill(digit), 'jpg'),cv.flip(annotated_image, 1)) # 保存
                #video.write(cv.flip(annotated_image, 1))

                for j in range(21):
                        array[42*n+j,3]=results.multi_hand_landmarks[0].landmark[j].x*w
                        array[42*n+j,4]=(1-results.multi_hand_landmarks[0].landmark[j].y)*h
                        array[42*n+j,5]=results.multi_hand_landmarks[0].landmark[j].z*w
                        array[42*n+21+j,3]=results.multi_hand_landmarks[1].landmark[j].x*w
                        array[42*n+21+j,4]=(1-results.multi_hand_landmarks[1].landmark[j].y)*h
                        array[42*n+21+j,5]=results.multi_hand_landmarks[1].landmark[j].z*w



            #顔の場合分け
            if type(results_f.multi_face_landmarks)!=type(None):
                for face_landmarks in results_f.multi_face_landmarks: # 画像内の全ての顔の顔特徴点


                    for j in range(468):
                        array_f[468*n+j,3]=(1-face_landmarks.landmark[j].x)*w
                        array_f[468*n+j,4]=(1-face_landmarks.landmark[j].y)*h
                        array_f[468*n+j,5]=face_landmarks.landmark[j].z*w


                #array2.append(hand_landmarks.landmark)
                    mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style())

                    #mp_drawing.draw_landmarks(
                    #image=annotated_image,
                    #landmark_list=face_landmarks,
                    #connections=mp_face_mesh.FACE_CONNECTIONS,
                    #landmark_drawing_spec=drawing_spec,
                    #connection_drawing_spec=drawing_spec) # 特徴点の描画



            #画像の保存

                cv.imwrite('{}_{}.{}'.format(base_path3, str(n).zfill(digit), 'jpg'),cv.flip(annotated_image, 1)) # 保存
                video_f.write(cv.flip(annotated_image, 1))
            else:

                for j in range(468):
                    array_f[468*n+j,3]=0
                    array_f[468*n+j,4]=0
                    array_f[468*n+j,5]=0


                ma=max(n-1,0)
                #array_f[n]=array_f[ma]
                cv.imwrite('{}_{}.{}'.format(base_path3, str(n).zfill(digit), 'jpg'),cv.flip(annotated_image, 1)) # 保存
                video_f.write(cv.flip(annotated_image, 1))
                #次のフレーム
            n += 1
            hands.close() # 毎回インスタンスを終了させる
            face_mesh.close() # 毎回インスタンスを終了させる


        #全フレーム読み込み完了
        else:

            #video出力
            video_f.release()
            #csv保存

            df=pd.DataFrame(array)
            df.to_csv(os.path.join(dir_path, 'hands.csv'), header=None, index = False)

            df_f=pd.DataFrame(array_f)
            df_f.to_csv(os.path.join(dir_path,'face.csv'),header=None, index = False)
            return messagebox.showinfo('処理終了しました', '完了')

# button3クリック時の処理
def button3_clicked():
    fTyp = [("","jpg"),("","png")]
    dir_path = file2.get()
    basename3 = 'hand_face'
    dirname = os.getcwd()

    iDir = os.path.join(os.path.join(dirname, dir_path),basename3)
    #iDir = os.path.abspath(os.path.dirname(__file__))
    #iDir = '.'
    filepath = filedialog.askopenfilename(filetypes = fTyp, initialdir = iDir)
    file3.set(filepath)#face_77.jpg

def button4_clicked(): #[距離計算開始]
    dir_path = file2.get()

    #最も良い顔画像
    s=file3.get()
    #文字列から数字取得
    resultnum = re.findall(r"\d+", s)
    num=int(resultnum[-1])

    print('Best:',num)


    #face.csv読み込み
    fa=pd.read_csv(os.path.join(dir_path, 'face.csv'),header=None,index_col=[0,1,2])
    fan=fa.loc[num]
    #199顎-4鼻=基準距離

    disv=fan.loc[1,199]-fan.loc[1,4]

    dis=np.linalg.norm(disv)

    #hand.csv読み込み
    ha=pd.read_csv(os.path.join(dir_path, 'hands.csv'),header=None,index_col=[0,1,2])
    ha=ha.iloc[:,:3].dropna()

    hb=copy.copy(ha)
    hb=hb.iloc[:,:0]
    hb['face_point']=999
    hb['face_part']='None'
    hb['distance_pixel']=9999

    pa=pd.read_csv('part.csv',header=None)


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
    df.to_csv(os.path.join(dir_path, 'hands.csv'), header=None)
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
    df.to_csv(os.path.join(dir_path, 'distance.csv'),header=None)

    return messagebox.showinfo('計算終了', '完了')

def button45_clicked():#[位置情報付与]
    dir_path = file2.get()
    basename4 = 'split'
    base_path4 = os.path.join(dir_path, basename4)

    #動画のFPS情報
    l2 = file1.get()
    cap = cv.VideoCapture(l2)
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    frr = cap.get(cv.CAP_PROP_FPS)
    #分割したものを動画化
    fourcc = cv.VideoWriter_fourcc('m','p','4', 'v')
    video_f  = cv.VideoWriter(os.path.join(dir_path,'hand_faceVideo2.mp4'), fourcc, frr, (w, h))

    l = glob.glob(os.path.join(base_path4,'*'))
    l.sort()
    real_m=len([name for name in os.listdir(base_path4) if os.path.isfile(os.path.join(base_path4, name))])
    print(real_m)

    #distance.csv読み込み
    da=pd.read_csv(os.path.join(dir_path, 'distance.csv'),header=None,index_col=[0,1,2])
    
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
        draw.text((size[0], size[1]), text1, font=font, fill='#FFF')
        draw.text((imagesize[0]-size[0]*3.5, size[1]), text0, font=font, fill='#FFF')
        draw.text((imagesize[0] - size[0], imagesize[1] - size[1]), text2, font=font, fill='#FFF')

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
    button1 = ttk.Button(root, text=u'動画を探す', command=button1_clicked)
    button1.grid(row=0, column=3)

    # ラベルの作成
    # 「ファイル」ラベルの作成
    s = StringVar()
    s.set('動画ファイルPath>>')
    label1 = ttk.Label(frame1, textvariable=s)
    label1.grid(row=0, column=0)

    # 参照ファイルパス表示ラベルの作成
    file1 = StringVar()
    file1_entry = ttk.Entry(frame1, textvariable=file1, width=50)
    file1_entry.grid(row=0, column=2)

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
    button2 = ttk.Button(frame3, text='骨格抽出開始', command=button2_clicked)
    button2.pack(side=LEFT)

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
