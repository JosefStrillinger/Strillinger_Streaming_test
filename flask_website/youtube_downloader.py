from youtube_dl import YoutubeDL
import ffmpeg
import os

class AudioDownloaderYouTube:

    def __init__(self, url_list):
        self.url_list = url_list
        self.params = None

    def set_params(self, audio_path, format_input='mp3'):
        self.params = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(audio_path, '%(title)s.' + format_input),
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format_input,
                'preferredquality': '192',
            }]
        }

    def get_info(self):
        with YoutubeDL({'quiet': True}) as audio:
            info = audio.extract_info(self.url_list[0], download=False)
            print('\nTITLE : ', info['title'], '\n')

    def download(self):
        with YoutubeDL(self.params) as audio:
            audio.download(self.url_list)