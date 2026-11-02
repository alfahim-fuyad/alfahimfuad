from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Profile
from .github_api import get_github_user, get_github_repos
from .cv_generator import build_cv_pdf

def home(request):
    profile = Profile.objects.first()

    # Prefer a photo uploaded in the admin. Otherwise fall back to the real
    # GitHub avatar for the configured profile, so the hero always shows an
    # actual picture instead of a broken/placeholder image.
    avatar_url = None
    if profile and profile.photo:
        avatar_url = profile.photo.url
    else:
        github_user = get_github_user()
        if github_user:
            avatar_url = github_user.get('avatar_url')

    return render(request, 'home/home.html', {'profile': profile, 'avatar_url': avatar_url})


def download_cv(request):
    """Generate a fresh, ATS-friendly CV PDF from live GitHub + portfolio data.

    Built on every request (not stored on disk), so it always reflects the
    latest GitHub repos, education entries, and admin-edited CV content with
    no manual regeneration step.
    """
    profile = Profile.objects.first()
    cv_url = request.build_absolute_uri()
    buf, filename = build_cv_pdf(profile, cv_url=cv_url)
    response = HttpResponse(buf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def github_stats(request):
    """Return live GitHub stats as JSON for the animated counter widget.

    Pulls the cached GitHub user + repos data (cached 30 min by
    github_api.py) and aggregates:
      - public_repos: total non-fork public repos
      - stars: total stars across all repos
      - forks: total forks across all repos
      - followers: from the GitHub user object

    The response is cached for 5 minutes on the client side via the
    browser's fetch cache to avoid hammering the server.
    """
    user = get_github_user() or {}
    repos = get_github_repos() or []

    total_stars = sum((r.get('stars') or 0) for r in repos)
    total_forks = sum((r.get('forks') or 0) for r in repos)
    # Filter out None values — repos might be None if the GitHub API
    # failed and the cache returned an empty list.
    repo_count = len(repos)

    data = {
        'public_repos': repo_count,
        'stars': total_stars,
        'forks': total_forks,
        'followers': user.get('followers', 0) if isinstance(user, dict) else 0,
        'following': user.get('following', 0) if isinstance(user, dict) else 0,
        'avatar_url': user.get('avatar_url') if isinstance(user, dict) else None,
        'ok': bool(user),
    }
    resp = JsonResponse(data)
    # Cache on the client for 5 minutes.
    resp['Cache-Control'] = 'public, max-age=300'
    return resp