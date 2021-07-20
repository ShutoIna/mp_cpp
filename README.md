#  C++版Mediapipeを用いた顔&手の3D座標取得と，手と顔の最短距離の計算

[Mediapipe](https://github.com/google/mediapipe)を用いた顔と手の座標を取得した後，指と顔の最短ポイントと最短距離を算出しています．

＊C++版を用いて行いました．

＊これはリアルタイム映像ではなく，すでに記録した映像で行っています．


## 実装の方法

### 1. [Mediapipe](https://github.com/google/mediapipe)のgitフォルダをクローン(またはDownload)

```
git clone https://github.com/google/mediapipe.git

```

### 2. 上のgitフォルダをclone(またはDownload)

```
git clone https://github.com/ShutoIna/mp_cpp.git

```


### 3. 1の以下のフォルダを，2のフォルダと置き換える

1. mediapipe/mediapipe/graphs　←　mp_cpp/graphs  
2. mediapipe/mediapipe/examples　←　mp_cpp/examples

として下さい．(以降は，1のmediapipeフォルダを利用)

### 4. 座標抽出

mediapipeフォルダまでコマンドラインで移動(cd mediapipe)


#### 4.1．手の座標

以下の2つのコマンドを実行すると，

```
bazel build -c opt --define MEDIAPIPE_DISABLE_GPU=1 mediapipe/examples/desktop/hand_tracking:hand_tracking_cpu

```

```
GLOG_logtostderr=1 bazel-bin/mediapipe/examples/desktop/hand_tracking/hand_tracking_cpu --calculator_graph_config_file=mediapipe/graphs/hand_tracking/hand_tracking_desktop_live.pbtxt --input_video_path=(入力動画のパス) --output_video_path=(出力動画のパス)

```

「**ID(整数)を入力して下さい ↓** 」という文字が現れます.  
適当な数字を入力してEnterを押すと，**'ID_hand.csv'がmediapipeフォルダ内に生成されます**

#### 4.2．顔の座標

以下の2つのコマンドを実行すると，

```
bazel build -c opt --define MEDIAPIPE_DISABLE_GPU=1 mediapipe/examples/desktop/face_mesh:face_mesh_cpu

```

```
GLOG_logtostderr=1 bazel-bin/mediapipe/examples/desktop/face_mesh/face_mesh_cpu --calculator_graph_config_file=mediapipe/graphs/face_mesh/face_mesh_desktop_live.pbtxt --input_video_path=(入力動画のパス) --output_video_path=(出力動画のパス)

```

「**ID(整数)を入力して下さい ↓** 」という文字が現れます.  
適当な数字を入力してEnterを押すと，**'ID_face.csv'がmediapipeフォルダ内に生成されます**


#### csvの説明

各csvの1行目は，動画の横サイズ(W)，縦サイズ(H)，総フレーム数(C)，fpsが表示されます．

2行目以降は，左から
1. フレーム数(1~C)
2. 左手(0)or右手(1)※顔のcsvでは全て0
3. インデックス(骨格番号)※手は0~20，顔は0~467
4. x座標(0~W)
5. y座標(0~H)
6. z座標(-W~W)

を表しています．

検出されないフレームに関しては，全ての座標を0としました．

例えば100フレームの動画の場合，100*42+1=4201行，100*468+1=46801行のcsvが生成されます．



### 5 距離計算
