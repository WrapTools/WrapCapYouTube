# youtube_example.py

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format = '%(name)s - %(levelname)s - %(message)s (line: %(lineno)d)',
    handlers=[
        logging.StreamHandler(),  # Log to console
        # logging.FileHandler('app.log')  # Log to file
    ]
)
from WrapCapYouTube.youtube_extractor import YouTubeContentExtractor

logger = logging.getLogger(__name__)

def main():
    url = input("Please enter a YouTube URL: ")
    try:
        extractor = YouTubeContentExtractor(url)

        # To download audio:
        audio_file = extractor.download_audio_local()
        logger.info(f"Audio File: {audio_file}")

        # To download the video
        video_file = extractor.download_video_local()
        logger.info(f"Video File: {video_file}")

        # To download transcript:
        transcript = extractor.download_transcript()
        print(transcript)

        info = extractor.get_info()
        logger.info(info)

    except ValueError as error:
        logger.error(f"Error: {error}")

if __name__ == "__main__":
    main()



# def main():
#     url = input("Please enter a YouTube URL: ")
#     try:
#         # url = 'https://www.youtube.com/watch?v=uaMmR8PIxkM&t=4s'
#         # url = 'https://www.youtube.com/watch?v=d9hWuLT53KU'
#         # url = 'https://www.youtube.com/watch?v=uT1PhcY0Xrg'
#         extractor = YouTubeContentExtractor(url)
#
#         # To download audio:
#         audio_file = extractor.download_audio_local()
#         print(f"Audio File: {audio_file}")
#
#         # To download the video
#         video_file = extractor.download_video_local()
#         print(f"Video File: {video_file}")
#
#         # To download transcript:
#         transcript = extractor.download_transcript()
#         print(transcript)
#
#         info = extractor.get_info()
#         print(info)
#
#     except ValueError as error:
#         print(f"Error: {error}")
#
#
#
# # Example usage:
# if __name__ == "__main__":
#     main()

"""
FUTURE
Security
# In your download_audio method:
basename = os.path.basename(output_file)
name, extension = os.path.splitext(basename)
safe_name = sanitize_filename(name)
safe_path = get_safe_file_path(f"{safe_name}.mp3")
validate_extension(safe_path)

# Proceed with saving the file to `safe_path`


import re

def sanitize_filename(filename):
    # Remove or replace characters that are not allowed in filenames.
    filename = re.sub(r'[\\/*?:"<>|]', "-", filename)  # Replacing invalid characters with "-"
    # Replacing spaces with "-"
    filename = re.sub(r'\s+', '-', filename)
    return filename

import os

DOWNLOAD_DIR = "/path/to/safe/download/directory"

def get_safe_file_path(basename):
    # Generate a safe file path within the download directory.
    sanitized_name = sanitize_filename(basename)
    safe_path = os.path.join(DOWNLOAD_DIR, sanitized_name)
    return safe_path

ALLOWED_EXTENSIONS = {'.mp3', '.mp4', '.txt'}

def validate_extension(filename):
    # Ensure the file has an allowed extension
    _, ext = os.path.splitext(filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Disallowed file extension: {ext}")



"""


