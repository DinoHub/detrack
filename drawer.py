import copy

import cv2


class Drawer:
    def __init__(self, color=(0, 0, 255), font=cv2.FONT_HERSHEY_DUPLEX):
        self.color = color
        self.font = font

    def draw(self, frame, track):
        frame_h, frame_w, _ = frame.shape
        l, t, r, b = [int(x) for x in track.to_ltrb(orig=True)]
        l = max(l, 0)
        t = max(t, 0)
        r = min(r, frame_w)
        b = min(b, frame_h)

        text = str(track.track_id)
        cv2.rectangle(frame, (l, t), (r, b), self.color, 2)
        cv2.putText(frame, 
                    text, 
                    (l+5, t+15),
                    self.font, 0.5, self.color, 1)
        return frame

    def draw_frame(self, frame, tracks):
        frame_dc = copy.deepcopy(frame)
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 0:
                continue
            self.draw(frame_dc, track)
        return frame_dc
