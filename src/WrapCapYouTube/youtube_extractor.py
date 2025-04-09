import re
import os
from pathlib import Path
import io
from urllib.parse import urlparse, parse_qs
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

import logging

# Logger Configuration
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

    # Helper methods
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

    def _get_download_directory(self):
        # Determine the default download directory based on the OS
        if os.name == 'nt':  # For Windows
            download_dir = Path.home() / 'Downloads'
        else:  # For Linux and macOS
            download_dir = Path.home() / 'Downloads'

        # Ensure the directory exists
        download_dir.mkdir(parents=True, exist_ok=True)
        return download_dir

    def _rename_file(self, file_path):
        # Generate a new file name by appending a counter if the file already exists
        counter = 1
        new_file_path = file_path.with_name(file_path.stem + f"_{counter}" + file_path.suffix)
        while new_file_path.exists():
            counter += 1
            new_file_path = file_path.with_name(file_path.stem + f"_{counter}" + file_path.suffix)
        return new_file_path

    # Download methods - memory
    def download_transcript(self, language='en'):
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(self.video_id, languages=[language])
            transcript_text = '\n'.join([snippet.text for snippet in transcript])
            return transcript_text
        except Exception as e:
            return str(e)

    def download_audio(self):
        try:
            yt = YouTube(self.url)
            audio = yt.streams.filter(only_audio=True).first()
            if not audio:
                logger.warning('No audio stream found!')
                return False

            audio.stream_to_buffer(self.mp3_file)
            self.mp3_file.seek(0)
            return True
        except Exception as e:
            logger.error(f'Failed to download audio for video {self.url} - {e}')
            return f"Error: {str(e)}"

    def download_video(self):
        try:
            yt = YouTube(self.url)
            video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            if not video:
                logger.warning('No suitable video stream found!')
                return False

            video.stream_to_buffer(self.mp4_file)
            self.mp4_file.seek(0)
            return True
        except Exception as e:
            logger.error(f'Failed to download audio for video {self.url} - {e}')
            return f"Error: {str(e)}"

    # Get methods
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
            logger.error(f'An error occurred while fetching video information: {e}')
            return {}

    # Download and save methods
    def download_audio_local(self):
        try:
            success = self.download_audio()
            if not success:
                return False  # If audio download fails, return False

            # Determine file name
            logger.info(f'Downloading audio stream for video: {self.url} ...')
            basename = f"{self.get_title()}.mp3"  # Use title for filename
            audio_file = re.sub(r'[\\/*?:"<>|]', "_", basename)  # Sanitize file name
            audio_file = re.sub(r'\s+', '-', audio_file)  # Replace spaces with hyphens

            # Determine path to save the file
            audio_file_path = self._get_download_directory() / audio_file
            if audio_file_path.exists():
                logger.warning(f"File {audio_file_path} already exists. Renaming...")
                audio_file_path = self._rename_file(audio_file_path)  # Rename if file exists

            # Save the file to disk
            with open(audio_file_path, 'wb') as f:
                f.write(self.mp3_file.getvalue())  # Write the buffer content to file

            logger.info(f"Audio saved as {audio_file_path}")
            return audio_file_path

        except Exception as e:
            logger.error(f'Failed to download audio for video {self.url} - {e}')
            return f"Error: {str(e)}"

    def download_video_local(self):
        try:
            success = self.download_video()
            if not success:
                return False  # If video download fails, return False

            # Determine file name
            logger.info(f'Downloading video stream: {self.url} ...')
            basename = f"{self.get_title()}.mp4"  # Use title for filename
            video_file = re.sub(r'[\\/*?:"<>|]', "_", basename)  # Sanitize file name
            video_file = re.sub(r'\s+', '-', video_file)  # Replace spaces with hyphens

            # Determine path to save the file
            video_file_path = self._get_download_directory() / video_file
            if video_file_path.exists():
                logger.warning(f"File {video_file_path} already exists. Renaming...")
                video_file_path = self._rename_file(video_file_path)  # Rename if file exists

            # Save the file to disk
            with open(video_file_path, 'wb') as f:
                f.write(self.mp4_file.getvalue())  # Write the buffer content to file

            logger.info(f"Video saved as {video_file_path}")
            return video_file_path

        except Exception as e:
            logger.error(f'Failed to download video for video {self.url} - {e}')
            return f"Error: {str(e)}"

    def download_transcript_local(self, language='en'):
        try:
            transcript_text = self.download_transcript()

            # Get the video title and sanitize it for use as a filename
            title = self.get_title()
            transcript_filename = re.sub(r'[\\/*?:"<>|]', "_", title)  # Replace forbidden characters
            transcript_filename = f"{transcript_filename}.txt"
            transcript_file_path = self._get_download_directory() / transcript_filename

            # Save the transcript to a local file
            with open(transcript_file_path, 'w', encoding='utf-8') as file:
                file.write(transcript_text)

            logger.info(f"Transcript saved as {transcript_file_path}")
            return transcript_file_path
        except Exception as e:
            logger.error(f'Failed to download transcript for video {self.url} - {e}')
            return f"Error retrieving transcript for video {self.url}: {str(e)}"
