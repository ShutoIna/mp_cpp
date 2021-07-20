#include <iostream>
#include <fstream>


#include <cstdlib>
#include <memory>
#include <vector>

#include "absl/flags/flag.h"
#include "absl/flags/parse.h"
#include "mediapipe/framework/calculator_framework.h"
#include "mediapipe/framework/formats/image_frame.h"
#include "mediapipe/framework/formats/image_frame_opencv.h"
#include "mediapipe/framework/port/file_helpers.h"
#include "mediapipe/framework/port/opencv_highgui_inc.h"
#include "mediapipe/framework/port/opencv_imgproc_inc.h"
#include "mediapipe/framework/port/opencv_video_inc.h"
#include "mediapipe/framework/port/parse_text_proto.h"
#include "mediapipe/framework/port/status.h"
#include "mediapipe/framework/formats/detection.pb.h"
#include "mediapipe/framework/formats/landmark.pb.h"
#include "mediapipe/framework/formats/rect.pb.h"

constexpr char kInputStream[] = "input_video";
constexpr char kOutputStream[] = "output_video";
constexpr char kWindowName[] = "MediaPipe";
//constexpr char kOutputDetections[] = "output_detections";
constexpr char kOutputLandmarks[] = "multi_face_landmarks";
//constexpr char kOutputPresence[] = "output_presence";

ABSL_FLAG(std::string, calculator_graph_config_file, "",
          "Name of file containing text format CalculatorGraphConfig proto.");
ABSL_FLAG(std::string, input_video_path, "",
          "Full path of video to load. "
          "If not provided, attempt to use a webcam.");
ABSL_FLAG(std::string, output_video_path, "",
          "Full path of where to save result (.mp4 only). "
          "If not provided, show result in a window.");

absl::Status RunMPPGraph() {
  std::string calculator_graph_config_contents;
  MP_RETURN_IF_ERROR(mediapipe::file::GetContents(
      absl::GetFlag(FLAGS_calculator_graph_config_file),
      &calculator_graph_config_contents));
  LOG(INFO) << "Get calculator graph config contents: "
            << calculator_graph_config_contents;
  mediapipe::CalculatorGraphConfig config =
      mediapipe::ParseTextProtoOrDie<mediapipe::CalculatorGraphConfig>(
          calculator_graph_config_contents);

  LOG(INFO) << "Initialize the calculator graph.";
  mediapipe::CalculatorGraph graph;
  MP_RETURN_IF_ERROR(graph.Initialize(config));

  LOG(INFO) << "Initialize the camera or load the video.";
  cv::VideoCapture capture;
  const bool load_video = !absl::GetFlag(FLAGS_input_video_path).empty();
  if (load_video) {
    capture.open(absl::GetFlag(FLAGS_input_video_path));
  } else {
    capture.open(0);
  }
  RET_CHECK(capture.isOpened());

  cv::VideoWriter writer;
  const bool save_video = !absl::GetFlag(FLAGS_output_video_path).empty();
  if (!save_video) {
    cv::namedWindow(kWindowName, /*flags=WINDOW_AUTOSIZE*/ 1);
#if (CV_MAJOR_VERSION >= 3) && (CV_MINOR_VERSION >= 2)
    capture.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    capture.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    capture.set(cv::CAP_PROP_FPS, 30);
#endif
  }
    //csv出力
       using std::endl;
       using std::ofstream;
    int a;
    std::cout << "ID(整数)を入力して下さい ↓ " << std::endl;
    std::cin >> a;
    ofstream ofs(std::to_string(a)+"_face.csv");


  LOG(INFO) << "Start running the calculator graph.";
  ASSIGN_OR_RETURN(mediapipe::OutputStreamPoller poller,
                   graph.AddOutputStreamPoller(kOutputStream));
  //ASSIGN_OR_RETURN(mediapipe::OutputStreamPoller poller_detections,
    //                   graph.AddOutputStreamPoller(kOutputDetections));
  ASSIGN_OR_RETURN(mediapipe::OutputStreamPoller poller_landmarks,
                   graph.AddOutputStreamPoller(kOutputLandmarks));
  ASSIGN_OR_RETURN(mediapipe::OutputStreamPoller poller_presence,
                   graph.AddOutputStreamPoller("landmark_presence"));
  //ASSIGN_OR_RETURN(mediapipe::OutputStreamPoller poller_presence,
    //                  graph.AddOutputStreamPoller(kOutputPresence));

  MP_RETURN_IF_ERROR(graph.StartRun({}));

  LOG(INFO) << "Start grabbing and processing frames.";
  bool grab_frames = true;
  int count = 0;
    // 幅
    int W = capture.get(CV_CAP_PROP_FRAME_WIDTH);
    // 高さ
    int H = capture.get(CV_CAP_PROP_FRAME_HEIGHT);
    // 総フレーム数
    int counts = capture.get(CV_CAP_PROP_FRAME_COUNT);
    // fps
    double fps = capture.get(CV_CAP_PROP_FPS);
    ofs << W << ", "<< H << ", "<< counts << ", "<<　fps << endl;

  while (grab_frames) {
      count += 1;

    // Capture opencv camera or video frame.
    cv::Mat camera_frame_raw;
    capture >> camera_frame_raw;
    if (camera_frame_raw.empty()) {
      if (!load_video) {
        LOG(INFO) << "Ignore empty frames from camera.";
        continue;
      }
      LOG(INFO) << "Empty frame, end of video reached.";
      break;
    }
    cv::Mat camera_frame;
    cv::cvtColor(camera_frame_raw, camera_frame, cv::COLOR_BGR2RGB);
    if (!load_video) {
      cv::flip(camera_frame, camera_frame, /*flipcode=HORIZONTAL*/ 1);
    }

    // Wrap Mat into an ImageFrame.
    auto input_frame = absl::make_unique<mediapipe::ImageFrame>(
        mediapipe::ImageFormat::SRGB, camera_frame.cols, camera_frame.rows,
        mediapipe::ImageFrame::kDefaultAlignmentBoundary);
    cv::Mat input_frame_mat = mediapipe::formats::MatView(input_frame.get());
    camera_frame.copyTo(input_frame_mat);

    // Send image packet into the graph.
    size_t frame_timestamp_us =
        (double)cv::getTickCount() / (double)cv::getTickFrequency() * 1e6;
    MP_RETURN_IF_ERROR(graph.AddPacketToInputStream(
        kInputStream, mediapipe::Adopt(input_frame.release())
                          .At(mediapipe::Timestamp(frame_timestamp_us))));

    // Get the graph result packet, or stop if that fails.
    mediapipe::Packet packet;
    mediapipe::Packet packet_presence;
    //mediapipe::Packet packet_detections;
    mediapipe::Packet packet_landmarks;

    if (!poller.Next(&packet)) break;
    auto &output_frame = packet.Get<mediapipe::ImageFrame>();
      // check whether the packet exists
    if (!poller_presence.Next(&packet_presence)) break;
    auto is_landmark_present = packet_presence.Get<bool>();
      LOG(INFO) <<"Frame: "<< count <<", "<<"Presence(N=0,Y=1): "<< is_landmark_present;
      //ofs << "Frame" << ", "<<　count << ", "<< "Presence" << ", "<<　is_landmark_present << endl;
      if (!is_landmark_present) {
            for (int ii = 0; ii <468 ; ++ii) {
                ofs << count << ", "<< 1 << ", "<< ii << ", "<< 0 << ", "<< 0 << ", "<< 0 << ", "<< endl;
        }
        }
    if (is_landmark_present) {
       // fetch landmarks only when they exist
       // if (poller_landmarks.Next(&packet_landmarks)) {
        if (!poller_landmarks.Next(&packet_landmarks) ) break;
              // do something
//            }
  //        }
    //auto &output_frame = packet.Get<mediapipe::ImageFrame>();
    auto &output_landmarks = packet_landmarks.Get<std::vector<mediapipe::NormalizedLandmarkList>>();
   // auto &output_detections = packet_detections.Get<std::vector<mediapipe::Detection>>();

    //add
    LOG(INFO) << "#Multi Face landmarks: " << output_landmarks.size();
   // LOG(INFO) << "#Multi Hand detections: " << output_detections.size();
    int hand_id = 0;
    for (const auto& single_hand_landmarks: output_landmarks) {

        //std::cout << output_detections[hand_id].DebugString();
        ++hand_id;
        LOG(INFO) << "Hand [" << hand_id << "]:";
        for (int i = 0; i < single_hand_landmarks.landmark_size(); ++i) {
          const auto& landmark = single_hand_landmarks.landmark(i);
    
            ofs <<count<<","<< hand_id << ", "<< i << ", "<< landmark.x()*W << ", "<< (1-landmark.y())*H << ", "<< landmark.z()*W << ", "<< endl;
        }
      }
    }
    // Convert back to opencv for display or saving.
    cv::Mat output_frame_mat = mediapipe::formats::MatView(&output_frame);
    cv::cvtColor(output_frame_mat, output_frame_mat, cv::COLOR_RGB2BGR);
    if (save_video) {
      if (!writer.isOpened()) {
        LOG(INFO) << "Prepare video writer.";
        writer.open(absl::GetFlag(FLAGS_output_video_path),
                    mediapipe::fourcc('a', 'v', 'c', '1'),  // .mp4
                    capture.get(cv::CAP_PROP_FPS), output_frame_mat.size());
        RET_CHECK(writer.isOpened());
      }
      writer.write(output_frame_mat);
    } else {
      cv::imshow(kWindowName, output_frame_mat);
      // Press any key to exit.
      const int pressed_key = cv::waitKey(5);
      if (pressed_key >= 0 && pressed_key != 255) grab_frames = false;
    }
    //}

  }

  LOG(INFO) << "Shutting down.";
  if (writer.isOpened()) writer.release();
  MP_RETURN_IF_ERROR(graph.CloseInputStream(kInputStream));
  return graph.WaitUntilDone();
}

int main(int argc, char** argv) {
  google::InitGoogleLogging(argv[0]);
  absl::ParseCommandLine(argc, argv);
  absl::Status run_status = RunMPPGraph();
  if (!run_status.ok()) {
    LOG(ERROR) << "Failed to run the graph: " << run_status.message();
    return EXIT_FAILURE;
  } else {
    LOG(INFO) << "Success!";
  }
  return EXIT_SUCCESS;
 }
