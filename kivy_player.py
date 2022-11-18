# take a look at this https://github.com/juniorliu95/hakkason_client/blob/309dbf1585463e6e828b93076b994c553eb9ef10/main.py

import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.video import Video

import time
import threading
import requests

import m3u8_player

class UniversalPlayer(App):
    def build(self):
        self.video = Video(source='prefetcharoni.ts')
        self.video.state='play'
        # self.video.options = {'eos': 'loop'}
        self.video.allow_stretch=True
        return self.video
    
    def change_source(self, source):
        self.video.source = source


def segment_download_and_show(url, save_path, player):
    print("opening it")

    prefetch_video = requests.get(url)

    open(save_path, "wb").write(prefetch_video.content)

    player.change_source(save_path)


def concurrent_loop(player):
    channel = "biagois"

    m3u8_handler = m3u8_player.m3u8Handler(f'https://www.twitch.tv/{channel}', twitch_low_latency=False)

    # print(f"found stream link for channel {channel}: {twitch_stream_link}")

    counter = 0

    while True:
        new_segment = m3u8_handler.get_new_segment_download_url()

        if new_segment != None:
            print("found it")
            counter += 1

            if (counter >= 10):
                break

            thread = threading.Thread(target=segment_download_and_show, args=(new_segment, f"prefetcharoni{m3u8_handler.sequence}.ts", player))
            thread.start()

        time.sleep(0.5)


if __name__ == '__main__':
    player = UniversalPlayer()

    thread = threading.Thread(target=concurrent_loop, args=(player, )) # args=(prefetch_file_url, )
    thread.start()

    player.run()

    print("hmm final")
