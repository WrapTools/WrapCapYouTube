import re
import os
import io
from urllib.parse import urlparse, parse_qs
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

import logging

# 2. Logger Configuration
logger = logging.getLogger(__name__)


class YouTubeContentExtractor:
    def __init__(self, url):
        self.url = url
        if not self._is_valid_youtube_url():
            raise ValueError('Invalid YouTube link!')

        self.video_id = self._get_youtube_video_id()
        self.mp3_file = io.BytesIO()
        self.mp4_file = io.BytesIO()
        self.title = None

    def _is_valid_youtube_url(self):
        valid_domains = ['youtube.com', 'youtu.be']
        return any(domain in self.url for domain in valid_domains)

    def _get_youtube_video_id(self):
        parsed_url = urlparse(self.url)
        if 'youtu.be' in self.url:
            return parsed_url.path.split('/')[1]
        else:
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [''])[0]

    def download_transcript(self, language='en'):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(self.video_id, languages=[language])
            transcript_text = '\n'.join([item['text'] for item in transcript])
            return transcript_text
        except Exception as e:
            return str(e)

    def download_audio(self):
        try:
            yt = YouTube(self.url)
            audio = yt.streams.filter(only_audio=True).first()
            if not audio:
                print('No audio stream found!')
                return False

            audio.stream_to_buffer(self.mp3_file)
            self.mp3_file.seek(0)
            return True
        except Exception as e:
            print(f'An error occurred: {e}')
            return False

    def download_video(self):
        try:
            yt = YouTube(self.url)
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if not video:
                print('No suitable video stream found!')
                return False

            video.stream_to_buffer(self.mp4_file)
            self.mp4_file.seek(0)
            return True
        except Exception as e:
            print(f'An error occurred: {e}')
            return False

    def get_mp3_file(self):
        if self.mp3_file.getbuffer().nbytes == 0:
            success = self.download_audio()
            if not success:
                return False
        return self.mp3_file

    def get_mp4_file(self):
        if self.mp4_file.getbuffer().nbytes == 0:
            success = self.download_video()
            if not success:
                return False
        return self.mp4_file

    def get_title(self):
        if self.title:
            return self.title
        else:
            all_info = self.get_info()
            return all_info['title']

    def download_audio_local(self):
        try:
            yt = YouTube(self.url)
            audio = yt.streams.filter(only_audio=True).first()
            if not audio:
                print('No audio stream found!')
                return False

            print('Downloading the audio stream ...', end='')
            output_file = audio.download()

            basename = os.path.basename(output_file)
            name, extension = os.path.splitext(basename)
            audio_file = f'{name}.mp3'
            audio_file = re.sub(r'\s+', '-', audio_file)

            os.rename(basename, audio_file)
            return audio_file
        except Exception as e:
            print(f'An error occurred: {e}')
            return False

    def download_video_local(self):
        try:
            yt = YouTube(self.url)
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if not video:
                print('No suitable video stream found!')
                return False

            print('Downloading the video stream ...', end='')
            output_file = video.download()
            print('Done!')
            return output_file
        except Exception as e:
            print(f'An error occurred: {e}')
            return False

    def get_info(self):
        try:
            yt = YouTube(self.url)
            info = {}

            attributes = [
                ('title', ''),
                ('views', 'Not available'),
                ('length', 'Not available'),
                ('description', ''),
                ('rating', 'Not available'),
                ('thumbnail_url', ''),
                ('publish_date', 'Not available'),
                ('author', 'Not available'),
                ('channel_id', 'Not available'),
                ('video_id', 'Not available'),
            ]

            for attr, default in attributes:
                try:
                    info[attr] = getattr(yt, attr, default)
                except AttributeError:
                    info[attr] = default
            self.title = info['title']
            return info
        except Exception as e:
            print(f'An error occurred while fetching video information: {e}')
            return {}


