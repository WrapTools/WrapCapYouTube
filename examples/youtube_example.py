# youtube_example.py

import logging

logging.basicConfig(
    level=logging.WARNING,
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
        transcript = extractor.download_transcript_local()
        logger.info(transcript)

        info = extractor.get_info()
        logger.info(info)

    except ValueError as error:
        logger.error(f"Error: {error}")

if __name__ == "__main__":
    main()
