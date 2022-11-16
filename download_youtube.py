# Loading all the packages required
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


if __name__ == '__main__':
    # Print a Welcome Message
    print('** YouTube to Audio Downloader **')

    # Setting value of c as 'n' to allow at least one iteration of the loop.
    c = 'n'

    # Looping till user does not enter a link as per his requirement.
    while c != 'y':
        url = input('\nEnter the Link of the YouTube Video: ')

        # Defining an instance of class and passing the URL as a list.
        ady = AudioDownloaderYouTube([url])

        # Obtaining the Title of the YouTube Video.
        ady.get_info()

        # Taking user input.
        c = input('To proceed, press `y`\nIf you want to enter the Link Again, press `n`\n: ')

    # Taking the Path where the Audio is to be downloaded and stored.
    audio_path = input('\nEnter path: ')

    # Available audio formats
    audio_formats = ['mp3', 'wav', 'aac', 'm4a']

    print('Choose a format from: \n\t*-', '\n\t*- '.join(audio_formats))
    format_input = input("Enter format: ")

    # Checking if the user has entered a correct format
    # If not then an exception is raised.
    if format_input in audio_formats:

        # Setting the value of params
        ady.set_params(audio_path, format_input)

        # If the format entered is correct then downloading operation is tried
        # If it fails then an exception is thrown
        try:
            ady.download()
            print('\n*Download Successful!*')
        except:
            print('\nDownload Could not be completed, Try Again!')
    else:
        raise ValueError('Audio Format Entered is Invalid')