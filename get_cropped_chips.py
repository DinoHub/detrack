import argparse
import datetime
import itertools
import math
import threading
import time
import traceback
from pathlib import Path

import cv2
import pkg_resources

from deep_sort_realtime.deepsort_tracker import DeepSort
from drawer import Drawer
from misc import draw_frame, save_chips
from scaledyolov4.scaled_yolov4 import ScaledYOLOV4


# change this for different video naming
def cam_name_func(file):
    # name = file.stem.split('_')[1]  # FRone
    # name = f"{file.parent.name.split('_')[0]}-{file.stem}" # NDP
    name = file.stem  # testvideo
    # print(f'name: {name}')
    return name


parser = argparse.ArgumentParser()
parser.add_argument('--vid_list', help='Path of text file containing all video paths, 1 in each row', type=str, required=True)
parser.add_argument('--context', help='Context of these set of videos (folder will be created in output dir)', type=str, required=True)
parser.add_argument('--seconds', help='Number of seconds between each chip save', type=int, default=1)
parser.add_argument('--infer_fps', help='FPS for inference', type=int, default=4)
parser.add_argument('--gpu_dev', help='Gpu device number to use. Default: 0', type=int, default=0)
parser.add_argument('--save_chips_dir', help='Path of output directory to save extracted chips', default=None)
parser.add_argument('--record_tracks_dir', help='Path of output directory to save inference video', default=None)
args = parser.parse_args()

seconds = args.seconds
context = args.context
infer_fps = args.infer_fps
classes_list = ['person']
crop_chips = bool(args.save_chips_dir)
record_tracks = bool(args.record_tracks_dir)

with open(args.vid_list) as f:
    input_vids = f.read().splitlines()
# print(input_vids)

od = ScaledYOLOV4(
        bgr=True,
        gpu_device=args.gpu_dev,
        # model_image_size=608,
        model_image_size=896,   # to detect mini hoomans
        # model_image_size=1280,
        # model_image_size=1536,
        max_batch_size=1,
        half=True,
        same_size=True,
        weights=pkg_resources.resource_filename('scaledyolov4', 'weights/yolov4-p6_-state.pt'),
        cfg=pkg_resources.resource_filename('scaledyolov4', 'configs/yolov4-p6.yaml'),
    )

drawer = Drawer(color=(255, 0, 0))

if crop_chips:
    chips_save_dir = Path(args.save_chips_dir) / f'{context}_crops'
    chips_save_dir.mkdir(parents=True, exist_ok=True)

start_whole = time.time()
for filename in input_vids:
    filename = Path(filename)
    vidcap = cv2.VideoCapture(str(filename))
    tracker = DeepSort(max_age=30, nn_budget=10)
    cam_name = cam_name_func(filename)

    fps = vidcap.get(cv2.CAP_PROP_FPS)
    fps = 25 if math.isinf(fps) else fps
    save_frame_skip = round(fps * seconds)
    vid_width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    infer_frame_skip = round(fps / infer_fps)
    print(f'{filename.stem} -- fps: {fps}, vid_width: {vid_width}, vid_height: {vid_height}, saving frame_skip: {save_frame_skip}, inference frame_skip: {infer_frame_skip}')

    if record_tracks:
        output_track_dir = Path(args.record_tracks_dir)
        output_track_dir.mkdir(parents=True, exist_ok=True)
        out_track_fp = output_track_dir / f'inference_{cam_name}.avi'
        out_track = cv2.VideoWriter(str(out_track_fp), cv2.VideoWriter_fourcc(*'MJPG'), infer_fps, (vid_width, vid_height))

    det_track_threads = {}

    start_vid = time.time()
    for frame_count in itertools.count():
        try:
            status, frame = vidcap.read()

            if not status: 
                break

            if (frame_count % infer_frame_skip == 0) or (frame_count % save_frame_skip == 0):
                all_detections = od.detect_get_box_in([frame], box_format='ltwh', classes=classes_list)[0]
                # print(f'all detections: {all_detections}')
                all_tracks = tracker.update_tracks(frame=frame, raw_detections=all_detections)
                # print(f'all tracks: {all_tracks}')

                if record_tracks:
                    threading.Thread(target=draw_frame, args=(frame, all_tracks, out_track, drawer), daemon=True).start()

                if (frame_count % save_frame_skip == 0) and crop_chips:
                    threading.Thread(target=save_chips, args=(frame, frame_count, all_tracks, chips_save_dir, cam_name), daemon=True).start()

        except Exception as e:
            traceback.print_exc()
            print(f'Error: {e}')
            print(f'Killing {cam_name}..')
            vidcap.release()
            if record_tracks:
                out_track.release()

        except KeyboardInterrupt:
            print(f'Interrupting {cam_name}..')
            vidcap.release()
            if record_tracks:
                out_track.release()

    time.sleep(0.1)
    vidcap.release()
    if record_tracks:
        out_track.release()
    seconds_taken = time.time() - start_vid
    time_taken = datetime.timedelta(seconds=seconds_taken)
    print(f'Time taken for {filename.stem}: {time_taken}')
    print(f'Avg FPS: {frame_count / seconds_taken}')
    print(f'Complete {cam_name}')

seconds_taken = time.time() - start_whole
time_taken = datetime.timedelta(seconds=seconds_taken)
print(f'Total time taken: {time_taken}')
