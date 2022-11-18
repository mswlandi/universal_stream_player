import requests
import streamlink
import os
import subprocess
import m3u8
import time
import threading


num_sequence = 0


def get_twitch_prefetch_segments(line, lineno, data, state):
    if line.startswith('#EXT-X-TWITCH-PREFETCH:'):
        custom_tag = line.split(':')
        if 'prefetch_urls' not in data:
            data['prefetch_urls'] = [":".join(custom_tag[1:]).strip()]
        else:
            data['prefetch_urls'].append(":".join(custom_tag[1:]).strip())


def segment_download_and_show(url, save_path):
    print("opening it")

    prefetch_video = requests.get(url)

    open(save_path, "wb").write(prefetch_video.content)

    subprocess.Popen(["celluloid", save_path])


class m3u8Handler():
    def __init__(self, stream_link, twitch_low_latency=False):
        # rudimentary check
        if twitch_low_latency and not "twitch.tv" in stream_link:
            raise Exception("twitch_low_latency turned up but stream URL is not from twitch")
        
        self.stream_url = streamlink.streams(stream_link)['best'].url
        self.sequence = 0
        self.twitch_low_latency = twitch_low_latency

        # self.stream_url = m3u8.load(twitch_stream_link, custom_tags_parser=m3u8Handler.get_twitch_prefetch_segments)


    def get_new_segment_download_url(self):
        '''returns the URL for the latest new segment. returns None if there are no new segments'''
        m3u8_data = m3u8.load(self.stream_url, custom_tags_parser=get_twitch_prefetch_segments).data

        if m3u8_data["media_sequence"] > self.sequence:
            self.sequence = m3u8_data["media_sequence"]

            if self.twitch_low_latency:
                try:
                    prefetch_file_url = m3u8_data["prefetch_urls"][-1]
                    return prefetch_file_url
                except KeyError as e:
                    file_url = m3u8_data["segments"][-1]["uri"]
                    return file_url
            else:
                # get latest normal segment
                file_url = m3u8_data["segments"][-1]["uri"]
                return file_url

        else:
            return None

    

if __name__ == '__main__':
    channel = "biagois"

    m3u8_handler = m3u8Handler(f'https://www.twitch.tv/{channel}', twitch_low_latency=False)

    # print(f"found stream link for channel {channel}: {twitch_stream_link}")

    counter = 0

    for i in range(500):
        new_segment = m3u8_handler.get_new_segment_download_url()

        if new_segment != None:
            print("found it")

            counter += 1
            if (counter >= 10):
                break

            thread = threading.Thread(target=segment_download_and_show, args=(new_segment, f"prefetcharoni{m3u8_handler.sequence}.ts"))
            thread.start()

        time.sleep(0.5)