import traceback
import sys
import streamlink
import threading

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstPbutils', '1.0')
gi.require_version('GObject', '2.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gst, GObject, GLib, GstPbutils

Gst.init(sys.argv)


def on_message(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
    mtype = message.type
    """
        Gstreamer Message Types and how to parse
        https://lazka.github.io/pgi-docs/Gst-1.0/flags.html#Gst.MessageType
    """
    if mtype == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()

    elif mtype == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(err, debug)
        loop.quit()
    elif mtype == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        print(err, debug)

    return True


class GstreamerTwitch:
    def __init__(self, twitch_channel):
        stream_url = streamlink.streams(f"https://www.twitch.tv/{twitch_channel}")['best'].url

        self._pipeline = Gst.Pipeline.new()

        # souphttpsrc location={url} -> hlsdemux -> decodebin -> videoconvert -> autovideosink
        #                                                     ╰> audioconvert -> autoaudiosink

        self._src = Gst.ElementFactory.make("souphttpsrc", "src")
        self._src.set_property("location", stream_url)
        self._src.set_property("is-live", "true")

        self._demux = Gst.ElementFactory.make("hlsdemux", "demux") # src pad sometimes present
        self._demux.connect("pad-added", self._on_pad_added)

        self._decode = Gst.ElementFactory.make("decodebin", "decode") # src pad sometimes present
        self._decode.connect("pad-added", self._on_pad_added)

        self._convert = Gst.ElementFactory.make("videoconvert", "convert")
        self._sink = Gst.ElementFactory.make("autovideosink", "sink")
        self._convert_audio = Gst.ElementFactory.make("audioconvert", "convert_audio")
        self._sink_audio = Gst.ElementFactory.make("autoaudiosink", "sink_audio")

        self._pipeline.add(self._src)
        self._pipeline.add(self._demux)
        self._pipeline.add(self._decode)
        self._pipeline.add(self._convert)
        self._pipeline.add(self._sink)
        self._pipeline.add(self._convert_audio)
        self._pipeline.add(self._sink_audio)

        self._src.link(self._demux)
        # self._demux.link(self._decode) # needs to be linked when src pad present
        # self._decode.link(self._convert) # needs to be linked when src pad present
        # self._decode.link(self._convert_audio) # needs to be linked when src pad present
        self._convert.link(self._sink)
        self._convert_audio.link(self._sink_audio)

        bus = self._pipeline.get_bus()
        bus.add_signal_watch()

        self._loop = GLib.MainLoop()
        bus.connect("message", on_message, self._loop)
        
    
    def start(self):
        """First play, loads main loop"""
        try:
            self._loop.run()
        except Exception:
            traceback.print_exc()
            self._loop.quit()


    def play(self):
        """Play"""
        self._pipeline.set_state(Gst.State.PLAYING)
    

    def stop(self):
        """after finishing playing, stop and delete resources"""
        # Stop Pipeline
        self._pipeline.set_state(Gst.State.NULL)
        del self._pipeline
    

    def _on_pad_added(self, src, new_pad):
        """identifies what pad was added to what element and links them approprietely"""

        print(f"Received new pad '{new_pad.get_name()}' from '{src.get_name()}'")

        if src.get_name() == "demux":
            ret = new_pad.link(self._decode.get_static_pad('sink'))
            if not ret == Gst.PadLinkReturn.OK:
                print(f"    FAIL to link with with decode")
            else:
                print(f"    linked pad with decode")
        
        if src.get_name() == "decode":
            if new_pad.get_name() == "src_0": # video
                ret = new_pad.link(self._convert.get_static_pad('sink'))
                if not ret == Gst.PadLinkReturn.OK:
                    print(f"    FAIL to link with with convert")
                else:
                    print(f"    linked pad with convert")
            
            elif new_pad.get_name() == "src_1": # audio
                ret = new_pad.link(self._convert_audio.get_static_pad('sink'))
                if not ret == Gst.PadLinkReturn.OK:
                    print(f"    FAIL to link with with convert_audio")
                else:
                    print(f"    linked pad with convert_audio")

if __name__ == "__main__":
    gst_twitch = GstreamerTwitch("limmy")
    gst_twitch.play()
    gst_twitch.start()
    gst_twitch.stop()

# TODO
# integrate player into kivy (make widget based on kivy/core/video/video_gstplayer.py)
# add controls to normal stream player
# create gstreamer pipeline for buffering and VOD recording
# generalize for other sources (other than twitch)
# gst-python reference:
#   https://github.com/GStreamer/gst-python/blob/master/examples/dynamic_src.py
#   https://github.com/happyleavesaoc/python-snapcast/blob/master/snapcast/client/gstreamer.py
#   https://github.com/gkralik/python-gst-tutorial/blob/master/basic-tutorial-3.py