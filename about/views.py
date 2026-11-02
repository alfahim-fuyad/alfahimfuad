from django.shortcuts import render
from .models import Education


DEFAULT_EDUCATION = [
    {
        'level': 'school',
        'level_label': 'School',
        'institution': 'Anjuman Adarsh Government High School',
        'degree': 'Secondary School Certificate (SSC)',
        'location': 'Netrakona, Bangladesh',
        'status': '',
        'website': '',
        # Static fallback image (used when no admin-uploaded image is set).
        'default_image': 'images/education/anjuman.png',
    },
    {
        'level': 'college',
        'level_label': 'College',
        'institution': 'Agricultural University College',
        'degree': 'Higher Secondary Certificate (HSC)',
        'location': 'Mymensingh, Bangladesh',
        'status': '',
        'website': 'https://www.aucm.edu.bd/',
        'default_image': 'images/education/aucm.png',
    },
    {
        'level': 'university',
        'level_label': 'University',
        'institution': 'East West University',
        'degree': 'Bachelor of Science in Computer Science & Engineering',
        'location': 'Dhaka, Bangladesh',
        'status': 'Currently Studying',
        'website': 'https://www.ewubd.edu/',
        'default_image': 'images/education/ewu.png',
    },
]


def _education_entries():
    """Return the built-in journey, with matching admin entries taking priority."""
    admin_entries = {
        entry.institution: entry
        for entry in Education.objects.all()
    }
    entries = []

    for default in DEFAULT_EDUCATION:
        entry = admin_entries.pop(default['institution'], None)
        if entry is None:
            entries.append(default)
            continue

        entries.append({
            'level': entry.level,
            'level_label': entry.get_level_display(),
            'institution': entry.institution,
            'degree': entry.degree or default['degree'],
            'location': entry.location or default['location'],
            'status': default['status'],
            'website': default['website'],
            'period': entry.period,
            'description': entry.description,
            'image': entry.image,
        })

    # Preserve any additional entries created in the admin after the defaults.
    for entry in admin_entries.values():
        entries.append({
            'level': entry.level,
            'level_label': entry.get_level_display(),
            'institution': entry.institution,
            'degree': entry.degree,
            'location': entry.location,
            'status': '',
            'website': '',
            'period': entry.period,
            'description': entry.description,
            'image': entry.image,
        })

    return entries


def about(request):
    educations = _education_entries()
    return render(request, 'about/about.html', {'educations': educations})
