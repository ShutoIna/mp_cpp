#  C++版Mediapipeを用いた顔&手の3D座標取得と，手と顔の最短距離の計算

### ※3/23 GUIに対応しました．
### ※5/13 mediapipeがアップデートしました&XYの計算に対応しました

[Mediapipe](https://github.com/google/mediapipe)を用いた顔と手の座標を取得した後，指と顔の最短ポイントと最短距離を算出しています．

＊C++版を用いて行いました．

＊これはリアルタイム映像ではなく，すでに記録した映像で行っています．



## 実装の方法

### 1. Mediapipeのgitフォルダをクローン(またはDownload)

```
git clone https://github.com/google/mediapipe.git

```

### 2. 上のgitフォルダをclone(またはDownload)

```
git clone https://github.com/ShutoIna/mp_cpp.git

```


### 3. 2のファイルを1のファイルと置き換える


### 4. 座標抽出

mp_cppまで移動


#### 4.1．手の座標

以下の2つのコマンドを実行すると，

```
bazel build -c opt --define MEDIAPIPE_DISABLE_GPU=1 mediapipe/examples/desktop/hand_tracking:hand_tracking_cpu

```

```
GLOG_logtostderr=1 bazel-bin/mediapipe/examples/desktop/hand_tracking/hand_tracking_cpu --calculator_graph_config_file=mediapipe/graphs/hand_tracking/hand_tracking_desktop_live.pbtxt --input_video_path=(入力動画のパス) --output_video_path=(出力動画のパス)


```

「**ID(整数)を入力して下さい ↓** 」という文字が現れます.  
適当な数字を入力してEnterを押すと，'ID_hand.csv'がmp_cppフォルダ内に生成されます

#### 4.2．顔の座標

以下の2つのコマンドを実行すると，

```
bazel build -c opt --define MEDIAPIPE_DISABLE_GPU=1 mediapipe/examples/desktop/face_mesh:face_mesh_cpu

```

```
GLOG_logtostderr=1 bazel-bin/mediapipe/examples/desktop/face_mesh/face_mesh_cpu --calculator_graph_config_file=mediapipe/graphs/face_mesh/face_mesh_desktop_live.pbtxt --input_video_path=(入力動画のパス) --output_video_path=(出力動画のパス)


```

「**ID(整数)を入力して下さい ↓** 」という文字が現れます.  
適当な数字を入力してEnterを押すと，'ID_face.csv'がmp_cppフォルダ内に生成されます


```
$ python gui.py

```


実行に成功すると，このような画面が出てくると思われます．


<img src="images/gui.png" width="600">
<!-- ![folder](images/gui.png "folder") -->


(GUI画面)



1. まずは，上二つの欄に解析したい動画，個人を紐付けるIDを入力してください．[骨格抽出開始]を押して実行させると，IDの名前がフォルダになり，諸々のファイル(csv,動画等)が作成されます．

    [ファイル構成]
    1. 元動画
    2. 手と顔の骨格付き動画(hand_face.mp4)
    3. 手と顔の骨格付き画像(hand_face/hand_face.jpg)
    4. 手のcsv(hand.csv)
    5. 顔のcsv(face.csv)



2. 次に，作成した顔画像から最も良く骨格が取れている画像を[顔フレーム検索]から選んでください．**また，距離計算方法について，Z軸の値を用いない場合はXYのラジオボタン，Z座標も用いる場合はXYZを選択してください．** 選んだ上で[距離計算開始]を実行させると，手と顔の距離のcsv(distance.csv)が生成されます．

    [最終的なファイル構成]
    1. 元動画
    2. 手と顔の骨格付き動画(hand_face.mp4)
    3. 手と顔の骨格付き画像(hand_face/hand_face.jpg)
    4. 手のcsv(hand.csv)
    5. 顔のcsv(face.csv)
    6. 手の各点，各フレームにおける，最も近い顔のポイント及び，距離のcsv(distance.csv)

3. 終了させたい時は終了ボタンを押してください，文字列を消去したい時は，リセットボタンを押してください．


ここで，大きなポイントとして，動画の保管場所はどこでも構いません．(GUIでどこからでも持ってこれるので)また，オリジナルの動画をコピーしたものをフォルダに入れています．尚，全てのcsvの行はフレーム数を指します．

○各csvの列の並び方について(見やすくするために()を使っています)
1. hand.csv (126列)
(左手1x, 左手2x...左手21x),  (左手1y, 左手2y...左手21y),  (左手1z, 左手2z...左21z),  (右手1x, 右手2x...右手21x),  (右手1y, 右手2y...右手21y),  (右手1z, 右手2z...右手21z)

2. face.csv (1404列)
 (顔1x, 顔2x, ..., 顔468x), (顔1y,顔2y,...顔468y), (顔1z,顔2z ...顔468z)

3. distance.csv (84列)
(左手1と最も近い顔の点&距離,左手2との最短点&距離...左手21との最短点&距離),  (右手1との最短点&距離,右手2との最短点&距離...右手21との最短点&距離)


※'左手1'とは，'左手の点1'を指す
※'左手1x'とは，'左手の点1のx座標'を指す
※'顔1x'とは，'顔の点1のx座標'を指す




○座標軸の取り方

<img src="images/axis.png" width="700">
<!-- ![folder](images/axis.png "Axis") -->


### realtime.py について

gui.pyと同様に

```
$ python realtime.py

```

**と入力するとPCのカメラが起動し，カメラ映像に手と顔の座標をリアルタイムで追加したものを出力しています．(座標取得&ビデオ保存は行っていません) 終了する際はQを押すことで終了します．**
