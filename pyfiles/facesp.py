import cv2
import os

def save_all_frames(ext='jpg'):
    dir_path='../Data/'
    a=input('IDを入力>> ')

    id_path=os.path.join(dir_path, a)
    video_path=os.path.join(id_path, str(a)+'_face.mov')
    video_path2=os.path.join(id_path, str(a)+'.mov')

    #格納フォルダのパスを通す
    face_path=os.path.join(id_path, 'face_pic')
    sp_path=os.path.join(id_path, 'pic')
    #フォルダ作成
    os.makedirs(face_path, exist_ok=True)
    os.makedirs(sp_path, exist_ok=True)

    #フォルダ内に入れる写真の名前
    base_path = os.path.join(face_path, 'face_pic')
    base_path2 = os.path.join(sp_path, 'pic')



    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return


    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    n = 0

    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('{}_{}.{}'.format(base_path, str(n).zfill(digit), ext), frame)
            n += 1
        else:
            break

    #元動画
    cap = cv2.VideoCapture(video_path2)

    if not cap.isOpened():
        return


    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    n = 0

    while True:
        ret, frame = cap.read()
        if ret:
            print(n)
            cv2.imwrite('{}_{}.{}'.format(base_path2, str(n).zfill(digit), ext), frame)
            n += 1
        else:
            return





if __name__ == '__main__':
    save_all_frames()
