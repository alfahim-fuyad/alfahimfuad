import logging

import requests

from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)

API_BASE = "https://api.github.com"

REQUEST_TIMEOUT = 15

# Cache successful GitHub responses for 30 minutes
CACHE_TIMEOUT = 60 * 30

# Cache failed responses for 10 minutes
ERROR_CACHE_TIMEOUT = 60 * 10


def github_headers():
    """
    Return headers for GitHub API requests.

    Uses GITHUB_TOKEN from environment variables when available.
    This increases the GitHub API rate limit compared with
    unauthenticated requests.
    """

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "FuadFolio",
    }

    token = getattr(settings, "GITHUB_TOKEN", None)

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def get_github_user(username=None):
    """
    Fetch the public GitHub profile.
    Uses cache to avoid unnecessary API requests.
    """

    username = username or settings.SITE_GITHUB_USERNAME

    cache_key = f"github_user:{username}"

    # Check cache first
    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    try:
        response = requests.get(
            f"{API_BASE}/users/{username}",
            headers=github_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        logger.info(
            "GitHub user API: status=%s username=%s",
            response.status_code,
            username,
        )

        response.raise_for_status()

        data = response.json()

        # Cache successful response
        cache.set(
            cache_key,
            data,
            CACHE_TIMEOUT,
        )

        return data

    except requests.RequestException as exc:

        logger.warning(
            "GitHub profile fetch failed for %s: %s",
            username,
            exc,
        )

        # Fallback data
        fallback = {
            "login": username,
            "avatar_url": None,
        }

        # Cache the fallback temporarily so that
        # every page request does not hit GitHub again.
        cache.set(
            cache_key,
            fallback,
            ERROR_CACHE_TIMEOUT,
        )

        return fallback


def get_github_repos(username=None):
    """
    Fetch public repositories from GitHub.

    - Newest pushed repositories first
    - Forked repositories excluded
    - Results cached for 30 minutes
    """

    username = username or settings.SITE_GITHUB_USERNAME

    cache_key = f"github_repos:{username}"

    # Check cache first
    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    try:
        response = requests.get(
            f"{API_BASE}/users/{username}/repos",
            params={
                "per_page": 100,
                "sort": "pushed",
                "direction": "desc",
            },
            headers=github_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        logger.info(
            "GitHub repos API: status=%s username=%s",
            response.status_code,
            username,
        )

        response.raise_for_status()

        raw_repositories = response.json()

        repositories = []

        for repo in raw_repositories:

            # Skip forked repositories
            if repo.get("fork"):
                continue

            repositories.append(
                {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "url": repo.get("html_url"),
                    "homepage": repo.get("homepage") or None,
                    "language": repo.get("language"),
                    "topics": repo.get("topics") or [],
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "updated_at": repo.get("pushed_at"),
                }
            )

        # Cache successful response
        cache.set(
            cache_key,
            repositories,
            CACHE_TIMEOUT,
        )

        return repositories

    except requests.RequestException as exc:

        logger.warning(
            "GitHub repos fetch failed for %s: %s",
            username,
            exc,
        )

        # Return empty list instead of repeatedly
        # requesting GitHub on every page load.
        fallback = []

        cache.set(
            cache_key,
            fallback,
            ERROR_CACHE_TIMEOUT,
        )

        return fallback