import re
import urllib.parse as urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled


async def process_url(message_str) -> str:
    url_list = extract_url(message_str)
    for url in url_list:
        if is_youtube_url(url):
            logger.info("▶️ Processing Youtube Transcript")
            url_data = get_FromVideoID(get_video_id(url))
        else:
            logger.info("🔗 Processing Standards Link")
            url_data = extract_text_from_url(url)
        message_str = message_str.replace(url, f"{url} (URL Content: {url_data})")
    return message_str


def extract_url(string) -> list:
    url_regex = re.compile(
        r"(?:(?:https?|ftp):\/\/)?"  # http:// or https:// or ftp://
        r"(?:\S+(?::\S*)?@)?"  # user and password
        r"(?:"  # IP address exclusion
        r"(?!(?:10|127)(?:\.\d{1,3}){3})"
        r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
        r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
        r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
        r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
        r"|"
        r"(?:www\.)?"  # www.
        r"(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+"  # domain name
        r"(?:\.(?:[a-z\u00a1-\uffff]{2,}))+"  # TLD identifier
        r"(?:\.(?:[a-z\u00a1-\uffff]{2,})+)*"
        r")"
        r"(?::\d{2,5})?"  # port
        r"(?:[/?#]\S*)?",  # resource path
        re.IGNORECASE,
    )
    return re.findall(url_regex, string)


def remove_url(text):
    url_regex = re.compile(r"https?://\S+")
    return url_regex.sub("", text)


def extract_text_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "Failed to retrieve the webpage"

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([paragraph.text for paragraph in paragraphs])
        return " ".join(text.split())
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return ""


def get_transcript_from_url(url):
    try:
        parsed_url = urlparse.urlparse(url)
        video_id = urlparse.parse_qs(parsed_url.query)["v"][0]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_list])
        return transcript
    except (KeyError, TranscriptsDisabled):
        return "Error retrieving transcript from YouTube URL"


def is_youtube_url(url):
    if url is None:
        return False
    youtube_regex = (
        r"(https?://)?(www\.)?"
        r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    )
    return re.match(youtube_regex, url) is not None


def get_video_id(url):
    parsed_url = urlparse.urlparse(url)
    if "youtube.com" in parsed_url.netloc:
        video_id = urlparse.parse_qs(parsed_url.query).get("v")
        if video_id:
            return video_id[0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path[1:] if parsed_url.path else None
    return "Unable to extract YouTube video and get text"


def get_FromVideoID(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_list])
        return transcript
    except (KeyError, TranscriptsDisabled):
        return "Error retrieving transcript from YouTube URL"
