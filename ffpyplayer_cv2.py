import cv2
import time
from ffpyplayer.player import MediaPlayer
import numpy as np

ff_opts = {
            'out_fmt': 'rgba',
            'sn': True
        }

def play_thing(filename):
    player = MediaPlayer(filename, thread_lib='SDL', ff_opts=ff_opts)

    while True:
        frame, val = player.get_frame()
        if val == 'eof': 
            break
        elif frame is None:
            time.sleep(0.01)
        elif val == 'paused':
            print("uhh pause")
        if frame is not None:
            image, pts = frame
            w, h = image.get_size()

            # # convert to array width, height
            # img = np.asarray(image.to_bytearray()[0]).reshape(h,w,3)

            # # convert RGB to BGR because `cv2` need it to display it
            # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            time.sleep(val) if val else time.sleep(1/60)
            # cv2.imshow('video', img)

            # if cv2.waitKey(1) & 0xff == ord('q'):
            #     break

    player.close_player()

play_thing("prefetcharoni5513.ts")
time.sleep(2)
play_thing("prefetcharoni5514.ts")
time.sleep(2)
play_thing("prefetcharoni5515.ts")
time.sleep(2)
play_thing("prefetcharoni5516.ts")
time.sleep(2)
play_thing("prefetcharoni5517.ts")
time.sleep(2)
play_thing("prefetcharoni5518.ts")
time.sleep(2)
play_thing("prefetcharoni5519.ts")
time.sleep(2)
play_thing("prefetcharoni5520.ts")
time.sleep(2)
play_thing("prefetcharoni5521.ts")