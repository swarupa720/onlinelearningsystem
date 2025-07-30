from django import template
import re
from collections.abc import Iterable  # Needed for safe iterable check

register = template.Library()

@register.filter
def youtube_embed(value):
    """
    Extract the YouTube video ID and convert to embed URL.
    Example: https://www.youtube.com/watch?v=abc123 -> https://www.youtube.com/embed/abc123
    """
    match = re.search(r'v=([a-zA-Z0-9_-]+)', value)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return value

@register.filter
def id_in_list(id_value, id_list):
    """
    Template filter to check if an ID exists in a list of IDs.
    Returns True if id_value is in id_list, else False.
    """
    if isinstance(id_list, Iterable) and not isinstance(id_list, (str, bytes)):
        return id_value in id_list
    return False
