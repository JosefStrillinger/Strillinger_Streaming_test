from __future__ import unicode_literals
import youtube_dl
import ffmpeg

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'output.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
    }],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    url=input("Enter Youtube URL: ")
    ydl.download([url])
    stream = ffmpeg.input('output.m4a')#youtube_dl.utils.DownloadError: ERROR: ffprobe/avprobe and ffmpeg/avconv not found. Please install one.
    stream = ffmpeg.output(stream, 'output.wav')