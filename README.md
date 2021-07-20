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


### 3. 1のファイルを2のファイルと置き換える

○ mediapipe/mediapipe/graphs　←　mp_cpp/graphs  
○ mediapipe/mediapipe/examples　←　mp_cpp/examples

として下さい．(以降は，1のmediapipeフォルダを利用)

### 4. 座標抽出

mediapipeフォルダまでコマンドラインで移動


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



### 5 距離計算
