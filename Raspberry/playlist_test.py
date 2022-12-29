import os
import pygame
from pygame import mixer

def start_playlist():
    global playlist
    old_songs = []
    mixer.music.load(playlist[0])
    old_songs.append(playlist[0])
    playlist.pop(0)
    mixer.music.play()
    mixer.music.queue(playlist[0])
    old_songs.append(playlist[0])
    playlist.pop(0)
    mixer.music.set_endevent(pygame.USEREVENT+1)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT+1:
                print("finished playing song")
                if len(playlist) > 0:
                    mixer.music.queue(playlist[0])
                    old_songs.append(playlist[0])
                    playlist.pop(0) 
            if not mixer.music.get_busy():#error here
                for i in range(len(old_songs)):
                    os.remove(old_songs[i])
                running = False
                break
            
def insert_into_playlist(dir_path, playlist):
    for file in os.listdir(dir_path):
        if file.endswith(".wav"):
            if file not in playlist:
                playlist.append(dir_path + "/" + file)            

if __name__ == "__main__":
    pygame.init()
    mixer.init()
    mixer.music.set_volume(0.1)
    playlist = []
    insert_into_playlist("Raspberry/received_samples", playlist)
    start_playlist()
    