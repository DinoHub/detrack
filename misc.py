import cv2


def draw_frame(frame, all_tracks, out_track, drawer):
    drawn_frame = drawer.draw_frame(frame, all_tracks)
    out_track.write(drawn_frame)


def save_chips(frame, frame_count, all_tracks, chips_save_dir, cam_name):
    # save all chips in chips_save_dir with camname_id_tracknum_framenum
    for track in all_tracks:
        if not track.is_confirmed() or track.time_since_update > 0:
            continue
        
        chip_path = chips_save_dir / f'{cam_name}_id_{track.track_id}_{frame_count}.jpg'

        frame_h, frame_w, _ = frame.shape
        l, t, r, b = [int(x) for x in track.to_ltrb(orig=True)]
        l = max(l, 0)
        t = max(t, 0)
        r = min(r, frame_w)
        b = min(b, frame_h)
        chip = frame[t:b, l:r]
        cv2.imwrite(str(chip_path), chip)
