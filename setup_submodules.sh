#!/usr/bin/env bash

# install scaledyolov4 and deep_sort_realtime submodules
cd ScaledYOLOv4 && pip3 install -e .
cd ../deep_sort_realtime && pip3 install -e .
