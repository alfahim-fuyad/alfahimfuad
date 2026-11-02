from django.shortcuts import render
from home.github_api import get_github_repos

from portfolio.models import Project


def _merge_with_admin(repos):
    """Merge live GitHub repos with admin-managed Project records.

    The admin Project model already has fields: title, description,
    image, project_url. We use it to OVERRIDE the placeholder thumbnail
    of a GitHub repo when a Project entry with the same title exists,
    and to ADD extra showcase projects that aren't on GitHub.

    The Project model itself is NOT changed — only read.
    """
    # Build an index keyed by the lower-cased title for case-insensitive
    # matching against GitHub repo names.
    admin_projects = list(Project.objects.all())
    by_title = {}
    standalone = []

    for p in admin_projects:
        key = (p.title or "").strip().lower()
        if key:
            by_title[key] = p
        else:
            standalone.append(p)

    merged_repos = []
    matched_ids = set()

    for repo in repos:
        key = (repo.get("name") or "").strip().lower()
        admin_entry = by_title.get(key)
        if admin_entry:
            matched_ids.add(admin_entry.id)
            repo = dict(repo)  # shallow copy so we don't mutate the cache
            repo["admin_image"] = (
                admin_entry.image.url if admin_entry.image else None
            )
            if admin_entry.description and not repo.get("description"):
                repo["description"] = admin_entry.description
            if admin_entry.project_url and not repo.get("homepage"):
                repo["homepage"] = admin_entry.project_url
            repo["has_admin_image"] = bool(admin_entry.image)
        else:
            repo["has_admin_image"] = False
        merged_repos.append(repo)

    # Standalone showcase projects (no matching GitHub repo).
    showcase = []
    for p in admin_projects:
        if p.id in matched_ids:
            continue
        showcase.append({
            "name": p.title,
            "description": p.description,
            "url": p.project_url or "",
            "homepage": p.project_url or None,
            "language": "",
            "topics": [],
            "stars": None,
            "forks": None,
            "updated_at": None,
            "admin_image": p.image.url if p.image else None,
            "has_admin_image": bool(p.image),
            "is_showcase": True,
        })

    return merged_repos, showcase


def portfolio(request):
    repos = get_github_repos()
    github_error = repos is None
    repos = repos or []

    merged_repos, showcase = _merge_with_admin(repos)

    return render(request, 'portfolio/portfolio.html', {
        'repos': merged_repos,
        'showcase': showcase,
        'github_error': github_error,
    })
