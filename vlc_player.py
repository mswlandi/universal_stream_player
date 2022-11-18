import vlc
import time
 
# creating a vlc instance
vlc_instance = vlc.Instance()
    
# creating a media player
# player = vlc_instance.media_player_new()
player = vlc_instance.media_list_player_new()
Media_list = vlc_instance.media_list_new()

media = vlc_instance.media_new("prefetcharoni5513.ts")
Media_list.add_media(media)
player.set_media_list(Media_list)
    
# play the video
player.play()

counter = 5514
medialist = []
for i in range(5522):
    # time.sleep(1.5)

    filename = f"prefetcharoni{counter + i}.ts"
    medialist.append(vlc_instance.media_new(filename))
    Media_list.add_media(medialist[-1])

Media_list.lock()

time.sleep(20)