from django.shortcuts import render

from home.models import Profile
from .models import Experience, Certification, Achievement
from .parsers import (
    parse_skill_categories,
    parse_simple_lines,
    parse_languages,
)


def others(request):
    """Render the professional "Others" page.

    Pulls together:
      - The owner's Profile (summary, skills, core competencies,
        languages, interests) — the same row that feeds the auto-
        generated CV.
      - Structured admin-managed rows for Experience, Certifications,
        and Achievements.
    """
    profile = Profile.objects.first()

    # --- Profile-derived content ---
    skill_categories = []
    core_competencies = []
    languages = []
    interests = []
    profile_summary = ""

    if profile:
        profile_summary = profile.summary or ""
        skill_categories = parse_skill_categories(profile.skills)
        core_competencies = parse_simple_lines(profile.core_competencies)
        languages = parse_languages(profile.languages)
        interests = parse_simple_lines(profile.interests)

    # --- Structured content from this app's models ---
    experiences = []
    for exp in Experience.objects.all():
        bullets = [
            line.strip()
            for line in (exp.description or "").splitlines()
            if line.strip()
        ]
        experiences.append({
            "role": exp.role,
            "organization": exp.organization,
            "period": exp.period,
            "location": exp.location,
            "bullets": bullets,
            "current": exp.current,
            "url": exp.url,
        })

    certifications = []
    for cert in Certification.objects.all():
        certifications.append({
            "title": cert.title,
            "issuer": cert.issuer,
            "date": cert.date,
            "credential_id": cert.credential_id,
            "url": cert.url,
            "image": cert.image.url if cert.image else "",
            "featured": cert.featured,
        })

    achievements = []
    for ach in Achievement.objects.all():
        achievements.append({
            "title": ach.title,
            "description": ach.description,
            "date": ach.date,
            "url": ach.url,
            "icon": ach.icon or "🏆",
        })

    # Owner name / title (used in the page header) — fall back to
    # env-driven defaults when no Profile row exists yet.
    from django.conf import settings
    owner_name = (profile.full_name if profile and profile.full_name
                  else getattr(settings, "SITE_FULL_NAME", ""))
    owner_title = (profile.title if profile and profile.title
                   else getattr(settings, "SITE_TITLE", ""))

    return render(request, "professional/professional.html", {
        "profile": profile,
        "owner_name": owner_name,
        "owner_title": owner_title,
        "profile_summary": profile_summary,
        "skill_categories": skill_categories,
        "core_competencies": core_competencies,
        "languages": languages,
        "interests": interests,
        "experiences": experiences,
        "certifications": certifications,
        "achievements": achievements,
        "has_experience": bool(experiences),
        "has_certs": bool(certifications),
        "has_achievements": bool(achievements),
        "has_skills": bool(skill_categories),
        "has_competencies": bool(core_competencies),
        "has_languages": bool(languages),
        "has_interests": bool(interests),
    })
