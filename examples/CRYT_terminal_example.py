# youtube_example.py

import logging
import sys

logging.basicConfig(
    level=logging.WARNING,
    format='%(name)s - %(levelname)s - %(message)s (line: %(lineno)d)',
    handlers=[
        logging.StreamHandler(),
    ]
)

from WrapCapYouTube.youtube_extractor import YouTubeContentExtractor

logger = logging.getLogger(__name__)

def show_help():
    print("Usage: python youtube_example.py [-a] [-v] [-t] [-h]")
    print("  -a   Download audio")
    print("  -v   Download video")
    print("  -t   Download transcript")
    print("  -h   Show help")
    sys.exit()

def parse_flags():
    valid_flags = {'a', 'v', 't', 'h'}
    flags = set()

    for arg in sys.argv[1:]:
        if arg.startswith("-") and len(arg) > 1:
            for char in arg[1:]:
                if char not in valid_flags:
                    print(f"Invalid flag: -{char}")
                    show_help()
                flags.add(char)
        else:
            print(f"Invalid argument: {arg}")
            show_help()

    return flags

def main():
    flags = parse_flags()

    if 'h' in flags:
        show_help()

    # If no flags, do all
    if not flags:
        flags = {'a', 'v', 't'}

    url = input("Please enter a YouTube URL: ")

    try:
        extractor = YouTubeContentExtractor(url)

        if 'a' in flags:
            audio_file = extractor.download_audio_local()
            logger.info(f"Audio File: {audio_file}")

        if 'v' in flags:
            video_file = extractor.download_video_local()
            logger.info(f"Video File: {video_file}")

        if 't' in flags:
            transcript = extractor.download_transcript_local()
            logger.info(transcript)

        info = extractor.get_info()
        logger.info(info)

    except ValueError as error:
        logger.error(f"Error: {error}")

if __name__ == "__main__":
    main()
