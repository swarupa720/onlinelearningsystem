from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(value):
    # Match video ID between v= and & or end of URL
    match = re.search(r'v=([a-zA-Z0-9_-]+)', value)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return value

@register.filter
def id_in_list(id_value, id_list):
    """Check if an ID exists in a list of IDs (e.g., completed lessons)."""
    return id_value in id_list
