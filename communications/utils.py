import re
from communications.models import ScreenedWord
import requests
from django.core.cache import cache
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from users.models import User
from users.serializers import SimpleUserSerializer

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"\+?\d[\d -]{8,14}\d"

def contains_restricted_content(message: str) -> tuple[str, bool]:
    """
    Replaces banned words/emails/phones with '*****' and flags message.

    Args:
        message (str): Input message.

    Returns:
        tuple: (sanitized_message, is_flagged)
    """
    flagged = False
    banned_words = ScreenedWord.objects.values_list("word", flat=True)

    for word in banned_words:
        if re.search(rf"(?i)\b{re.escape(word)}\b", message):
            message = re.sub(
                rf"(?i)\b{re.escape(word)}\b", "*****", message
            )
            flagged = True

    if re.search(EMAIL_REGEX, message) or re.search(PHONE_REGEX, message):
        message = re.sub(EMAIL_REGEX, "*****", message)
        message = re.sub(PHONE_REGEX, "*****", message)
        flagged = True


    # File-like URL detection
    FILE_LINK_REGEX = r"https?://[^\s]+\.(pdf|docx|xlsx|zip|rar|pptx?)"
    if re.search(FILE_LINK_REGEX, text, re.IGNORECASE):
        text = re.sub(FILE_LINK_REGEX, "*****", text)
        flagged = True

    return message, flagged


def extract_first_link(text: str) -> str | None:
    """Extracts the first URL from a given text."""
    url_regex = r"(https?://[^\s]+)"
    match = re.search(url_regex, text)
    return match.group(0) if match else None


def generate_preview_metadata(url):
    cache_key = f"preview:{url}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        res = requests.get(url, timeout=3)
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.title.string.strip() if soup.title else None
        description = soup.find("meta", attrs={"name": "description"}) or \
                      soup.find("meta", attrs={"property": "og:description"})
        image = soup.find("meta", attrs={"property": "og:image"})
        
        metadata = {
            "title": title,
            "description": description["content"] if description and description.has_attr("content") else "",
            "image": image["content"] if image and image.has_attr("content") else "",
        }
        cache.set(cache_key, metadata, timeout=3600 * 6)  # Cache for 6 hours
        return metadata
    except Exception:
        return None
    


async def get_user_data(user_ids):
    users = User.objects.filter(id__in=user_ids).select_related("profile")
    return SimpleUserSerializer(users, many=True).data