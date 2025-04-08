# WrapCapPDF/__init__.py

import logging

# Create a logger for your library
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# __all__ = ['']

from .youtube_extractor import YouTubeContentExtractor
