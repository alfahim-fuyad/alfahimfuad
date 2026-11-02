from django.shortcuts import render

from .models import Game, VideoLink
from .embed_utils import embed_url, youtube_thumbnail


def my_world(request):
    """Render the My World page: personal games + video links.

    (Renamed from "Others" — the new "Others" page is the professional
    one, mounted at /others/ by the `professional` app.)
    """
    games = list(Game.objects.all())

    # Pre-compute embeddable URLs and resolved thumbnails so the template
    # stays dumb and doesn't do URL parsing.
    games_ctx = []
    for g in games:
        games_ctx.append({
            "id": g.id,
            "title": g.title,
            "description": g.description,
            "embed_url": g.embed_url,
            "image": g.image.url if g.image else "",
            "play_label": g.play_label or "Play Now",
            "featured": g.featured,
        })

    videos = list(VideoLink.objects.all())
    videos_ctx = []
    for v in videos:
        thumb = v.thumbnail.url if v.thumbnail else (youtube_thumbnail(v.video_url) or "")
        videos_ctx.append({
            "id": v.id,
            "title": v.title,
            "description": v.description,
            "watch_url": v.video_url,
            "embed_url": embed_url(v.video_url),
            "thumbnail": thumb,
            "duration": v.duration,
            "featured": v.featured,
        })

    return render(request, "others/myworld.html", {
        "games": games_ctx,
        "videos": videos_ctx,
        "has_games": bool(games_ctx),
        "has_videos": bool(videos_ctx),
    })
