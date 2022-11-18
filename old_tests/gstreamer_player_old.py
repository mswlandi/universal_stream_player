import traceback
import sys
import streamlink

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstPbutils', '1.0')
gi.require_version('GObject', '2.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gst, GObject, GLib, GstPbutils

Gst.init(0)

# souphttpsrc location={url} ! hlsdemux ! decodebin ! audioconvert ! autoaudiosink


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


stream_url = streamlink.streams("https://www.twitch.tv/snowmarite")['best'].url

# print(stream_url)

pipeline = Gst.Pipeline.new()

src = Gst.ElementFactory.make("souphttpsrc")
src.set_property("location", stream_url)
src.set_property("is-live", "true")
demux = Gst.ElementFactory.make("hlsdemux") # src pad sometimes present
decode = Gst.ElementFactory.make("decodebin") # src pad sometimes present
convert = Gst.ElementFactory.make("audioconvert")
sink = Gst.ElementFactory.make("autoaudiosink")

pipeline.add(src)
pipeline.add(demux)
pipeline.add(decode)
pipeline.add(convert)
pipeline.add(sink)

src.link(demux)
demux.link(decode)
decode.link(convert)
convert.link(sink)

# https://lazka.github.io/pgi-docs/Gst-1.0/classes/Bus.html
bus = pipeline.get_bus()

# allow bus to emit messages to main thread
bus.add_signal_watch()

# Start pipeline
pipeline.set_state(Gst.State.PLAYING)

# Init GLib loop to handle Gstreamer Bus Events
loop = GLib.MainLoop()

# Add handler to specific signal
# https://lazka.github.io/pgi-docs/GObject-2.0/classes/Object.html#GObject.Object.connect
bus.connect("message", on_message, loop)

try:
    loop.run()
except Exception:
    traceback.print_exc()
    loop.quit()

# Stop Pipeline
pipeline.set_state(Gst.State.NULL)
del pipeline