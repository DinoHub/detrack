# DeTrack (Detect + Tracking)

## Introduction

"Sample" project that uses ScaledYOLOv4 and DeepSORT as packages on a video file, with option to save out human crops and inference video.

## Install

- Build Dockerfile and `./run_docker.sh`
- Clone [ScaledYOLOv4](https://github.com/yhsmiley/ScaledYOLOv4/tree/yolov4-large-dev) and [DeepSORT](https://github.com/levan92/deep_sort_realtime) repos on your machine (and download the weights)
- Inside docker, run `./setup_packages.sh` (decide if you want to install the packages as editable)

## Run

- Change the `cam_name_func` in `main.py` so that all videos in `vid_list` end up with a unique name.
- TADAA!
