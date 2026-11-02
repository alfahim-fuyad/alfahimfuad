"""
Helpers for turning raw video URLs into embeddable form.

Supports:
* YouTube watch URLs        — https://www.youtube.com/watch?v=ID
* YouTube short URLs        — https://youtu.be/ID
* YouTube playlist URLs     — https://www.youtube.com/playlist?list=ID
* YouTube embed URLs        — https://www.youtube.com/embed/ID
* Vimeo URLs                — https://vimeo.com/ID
* Anything else             — returned as-is (assumed already embeddable).
"""

from urllib.parse import urlparse, parse_qs, urlencode


def youtube_id(url):
    """Return the 11-char YouTube video ID for a URL, or None."""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    path = parsed.path or ""

    if host.endswith("youtu.be"):
        # youtu.be/ID
        return path.strip("/").split("/")[0] or None

    if "youtube.com" in host:
        if path.startswith("/watch"):
            qs = parse_qs(parsed.query)
            ids = qs.get("v")
            return ids[0] if ids else None
        if path.startswith("/embed/"):
            return path.split("/")[2] if len(path.split("/")) > 2 else None
        if path.startswith("/shorts/"):
            return path.split("/")[2] if len(path.split("/")) > 2 else None

    return None


def youtube_playlist_id(url):
    """Return a YouTube playlist ID, or None."""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if "youtube.com" not in host:
        return None
    qs = parse_qs(parsed.query)
    lists = qs.get("list")
    return lists[0] if lists else None


def vimeo_id(url):
    """Return a Vimeo numeric video ID, or None."""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if "vimeo.com" not in host or host.startswith("player."):
        return None
    parts = [p for p in (parsed.path or "").split("/") if p]
    # /12345678  or  /channels/x/12345678
    if parts and parts[-1].isdigit():
        return parts[-1]
    return None


def embed_url(video_url):
    """Convert a watch URL into an embeddable URL."""
    if not video_url:
        return ""

    # YouTube
    yid = youtube_id(video_url)
    if yid:
        pl = youtube_playlist_id(video_url)
        qs = {}
        if pl:
            qs["list"] = pl
        query = ("?" + urlencode(qs)) if qs else ""
        return f"https://www.youtube.com/embed/{yid}{query}"

    # Vimeo
    vid = vimeo_id(video_url)
    if vid:
        return f"https://player.vimeo.com/video/{vid}"

    # Already an embed URL or other provider — pass through.
    return video_url


def youtube_thumbnail(video_url):
    """Return a YouTube thumbnail URL for a video, or None."""
    yid = youtube_id(video_url)
    if not yid:
        return None
    return f"https://i.ytimg.com/vi/{yid}/hqdefault.jpg"
