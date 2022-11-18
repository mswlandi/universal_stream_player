from twitchrealtimehandler import (TwitchAudioGrabber, TwitchImageGrabber)
import time
import cv2
import queue
import threading
import os


buffer = queue.Queue()
channel = "alanzoka"
quality = "480p"
fps = 30
terminate = threading.Event()
clear = threading.Event()

def image_grabber_worker():
    image_grabber = TwitchImageGrabber(
        twitch_url=f"https://www.twitch.tv/{channel}",
        quality=quality,
        blocking=True,
        rate=f"{fps}"
        )
    
    while not terminate.is_set():
        img = image_grabber.grab()

        # if commanded to clear, do it just before receiving a new frame
        if clear.is_set():
            buffer.queue.clear()
            clear.clear()
        
        if img is not None:
            buffer.put(img)
    
    print("grabber thread closing")


thread = threading.Thread(target=image_grabber_worker, daemon=True)
thread.start()

previous_time = time.time()

while True:
    img = buffer.get(block=True)

    buffer_size = buffer.qsize() * img.size * img.itemsize
    print(f"size of buffer: {buffer_size / 1024} kb")

    cv2.imshow("frame", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # close if pressed Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        terminate.set()
        break

    # get to live time if pressed L
    if cv2.waitKey(1) & 0xFF == ord('l'):
        clear.set()

    # close if buffer size gets to 512MB
    if (buffer_size >= 1024*1024*512):
        terminate.set()
        break

    period = time.time()-previous_time
    # print(f'fps: {1/period}')

    sleep_time = 1/fps - period # wait for amount of time necessary to hit desired FPS
    if sleep_time > 0:
        time.sleep(sleep_time)
    print(f"actual FPS: {int(1/sleep_time)}")

    previous_time = time.time()

thread.join()