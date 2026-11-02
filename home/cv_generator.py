"""
generate_cv.py
==============
Generates a professional, ATS-friendly, two-column CV/resume as a PDF —
dark photo sidebar on the left (Contact / Skills / Languages / Hobbies)
and a white main column on the right (Profile / Work Experience /
Education), matching a common "modern resume" template.

HOW TO USE
----------
1. Install the one dependency this needs:
       pip install reportlab
   (Pillow is optional — only needed if you want a circular photo.
   It usually comes bundled with reportlab's dependencies, but if not:
       pip install Pillow)

2. Edit the CV_DATA dictionary below with your own information.
   - Set "photo" to the path of a photo file (jpg/png), or None to
     skip the photo and show initials instead.

3. Run it:
       python generate_cv.py

   It will create "My-CV.pdf" (or "<Name>-CV.pdf") in the same folder.
"""

import io
import os

# ---------------------------------------------------------------------
# 1) EDIT YOUR DATA HERE
# ---------------------------------------------------------------------
CV_DATA = {
    "name": "Your Name",
    "title": "Software Engineer",
    "photo": None,  # e.g. "photo.jpg" — or None for an initials placeholder

    "contact": {
        "Phone": "+1 234 567 890",
        "Email": "youremail@gmail.com",
        "Address": "#1 Street, City, State",
    },

    "skills": [
        "SQL Database Management",
        "Linux/Unix Command Line",
        "Python",
        "Java",
    ],

    "languages": [
        ("English", "Proficient"),
        ("Hindi", "Proficient"),
    ],

    "hobbies": ["Writing", "Cricket", "Photography"],

    "profile": (
        "I am a software engineer with experience in a variety of "
        "programming languages and a track record of delivering "
        "high-quality code. I am a strong communicator with a "
        "background in computer science, and I enjoy working "
        "collaboratively with others."
    ),

    "experience": [
        {
            "role": "Senior Software Developer",
            "company": "Company Name",
            "duration": "Jan 2019 - Dec 2023",
            "bullets": [
                "Developed and maintained websites using Java, Python, and C++.",
                "Led cross-functional teams to deliver successful software projects.",
                "Wrote a strong technical team to ensure quality of software delivered.",
            ],
        },
        {
            "role": "Web Developer",
            "company": "Company Name",
            "duration": "Jan 2021 - Dec 2021",
            "bullets": [
                "Developed and maintained websites using applications using languages "
                "such as HTML, CSS, JavaScript, and PHP.",
                "Worked with cross-functional teams to gather requirements and design "
                "user interfaces.",
            ],
        },
    ],

    "education": [
        {
            "degree": "Masters in Software Engineering",
            "institution": "XYX University, Bangalore",
            "duration": "Jan 2019 - Dec 2020",
        },
        {
            "degree": "Bachelor in Computer Science",
            "institution": "XYX University, Bangalore",
            "duration": "Jan 2015 - Dec 2018",
        },
    ],
}


# ---------------------------------------------------------------------
# 2) PDF BUILDING LOGIC — you shouldn't need to touch this part
# ---------------------------------------------------------------------

# --- palette (dark charcoal sidebar + a single accent color) ---------
INK = "#1f2430"
DIM = "#5b6472"
ACCENT = "#3a4cc9"
SIDEBAR_BG = "#23262e"
SIDEBAR_TEXT = "#f3f4f7"
SIDEBAR_DIM = "#aab0bd"
SIDEBAR_LINE = "#343844"
RULE = "#d9dce3"

SIDEBAR_W = 185


def _circular_photo(path):
    """Returns a BytesIO PNG with a circular crop of the photo, or None."""
    if not path or not os.path.exists(path):
        return None
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None

    img = Image.open(path).convert("RGBA")
    size = min(img.size)
    left = (img.width - size) // 2
    top = (img.height - size) // 2
    img = img.crop((left, top, left + size, top + size)).resize((300, 300))

    mask = Image.new("L", (300, 300), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 300, 300), fill=255)

    out = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask=mask)

    buf = io.BytesIO()
    out.save(buf, format="PNG")
    buf.seek(0)
    return buf


def build_cv_data(profile):
    """Build the data dict for build_cv_pdf from a Profile model + live data.

    Pulls from:
      - the Profile row (name, title, summary, skills, experience,
        languages, interests, photo, phone, location, website)
      - the about.Education model (for the education section)
      - Django settings (SITE_EMAIL, SITE_FULL_NAME, SITE_TITLE as
        fallbacks when no Profile row exists)

    Returns a dict in the format build_cv_pdf expects.
    """
    from django.conf import settings

    # Lazy imports to avoid circular import issues.
    try:
        from about.models import Education
    except Exception:
        Education = None

    name = (profile.full_name if profile and profile.full_name
            else getattr(settings, "SITE_FULL_NAME", "Al Fahim Fuad"))
    title = (profile.title if profile and profile.title
             else getattr(settings, "SITE_TITLE", ""))

    # Contact
    contact = {}
    if profile:
        if profile.phone:
            contact["Phone"] = profile.phone
        if profile.website:
            contact["Website"] = profile.website
    contact["Email"] = getattr(settings, "SITE_EMAIL", "")
    contact["Address"] = (profile.location if profile and profile.location
                          else "Dhaka, Bangladesh")

    # Skills — parse from Profile.skills text.
    # Format: one category per line, "Category: item1, item2"
    skills = []
    if profile and profile.skills:
        for line in profile.skills.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                _, items = line.split(":", 1)
                for item in items.split(","):
                    item = item.strip()
                    if item:
                        skills.append(item)
            else:
                skills.append(line)
    if not skills:
        skills = ["Python", "SQL", "Django", "JavaScript",
                  "Machine Learning", "Data Analysis"]

    # Languages — parse from Profile.languages ("Language: Level" per line)
    languages = []
    if profile and profile.languages:
        for line in profile.languages.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                lang, level = line.split(":", 1)
                languages.append((lang.strip(), level.strip()))
            else:
                languages.append((line, ""))
    if not languages:
        languages = [("English", "Professional"), ("Bengali", "Native")]

    # Hobbies / interests
    hobbies = []
    if profile and profile.interests:
        for line in profile.interests.replace(",", "\n").splitlines():
            h = line.strip()
            if h:
                hobbies.append(h)

    # Profile summary
    profile_text = (profile.summary if profile and profile.summary
                    else "Data Scientist and ML Engineer passionate about "
                         "building intelligent systems end-to-end.")

    # Experience — parse from Profile.experience.
    # Format: blocks separated by a blank line. First line of each block:
    # "Role | Organization | Date range". Following lines are bullets.
    experience = []
    if profile and profile.experience:
        blocks = profile.experience.split("\n\n")
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if not lines:
                continue
            first = lines[0]
            parts = first.split("|")
            entry = {
                "role": parts[0].strip() if len(parts) > 0 else "",
            }
            if len(parts) > 1:
                entry["company"] = parts[1].strip()
            if len(parts) > 2:
                entry["duration"] = parts[2].strip()
            entry["bullets"] = lines[1:]
            experience.append(entry)

    # Education — from about.Education model
    education = []
    if Education:
        try:
            for edu in Education.objects.all():
                education.append({
                    "degree": edu.degree or "",
                    "institution": edu.institution,
                    "duration": edu.period or "",
                })
        except Exception:
            pass
    if not education:
        education = [
            {
                "degree": "BSc in Computer Science & Engineering",
                "institution": "East West University, Dhaka",
                "duration": "Present",
            },
        ]

    # Photo — local file path (Cloudinary images are skipped; the CV
    # shows an initials placeholder instead).
    photo = None
    if profile and profile.photo:
        try:
            photo = profile.photo.path
        except (NotImplementedError, ValueError, AttributeError):
            photo = None

    return {
        "name": name,
        "title": title,
        "photo": photo,
        "contact": contact,
        "skills": skills,
        "languages": languages,
        "hobbies": hobbies,
        "profile": profile_text,
        "experience": experience,
        "education": education,
    }


def build_cv_pdf(data, output_path=None):
    """Build a CV PDF from the data dict.

    Parameters:
        data         dict with keys: name, title, photo, contact, skills,
                     languages, hobbies, profile, experience, education
        output_path  optional filename — if given, the PDF is ALSO saved
                     to that file (used by the standalone CLI). The PDF
                     is always built into an in-memory buffer regardless.

    Returns:
        (buffer, filename) — buffer is a BytesIO positioned at 0,
        filename is a safe download filename derived from the name.
    """
    import io

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
        Table, TableStyle, NextPageTemplate, KeepTogether,
    )

    PAGE_W, PAGE_H = A4
    MARGIN = 16 * mm
    SB_W = SIDEBAR_W

    name = data.get("name", "Your Name")
    title = data.get("title", "")
    contact = data.get("contact", {})
    skills = data.get("skills", [])
    languages = data.get("languages", [])
    hobbies = data.get("hobbies", [])
    profile = data.get("profile", "")
    experience = data.get("experience", [])
    education = data.get("education", [])

    photo_buf = _circular_photo(data.get("photo"))

    # ---------- styles ----------
    styles = {
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12,
                              textColor=colors.HexColor(ACCENT), leading=14,
                              spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.3,
                                leading=14, textColor=colors.HexColor(INK)),
        "item_title": ParagraphStyle("item_title", fontName="Helvetica-Bold",
                                      fontSize=10, textColor=colors.HexColor(INK),
                                      leading=13),
        "item_sub": ParagraphStyle("item_sub", fontName="Helvetica-Oblique",
                                    fontSize=8.6, textColor=colors.HexColor(DIM),
                                    leading=12),
        "item_date": ParagraphStyle("item_date", fontName="Helvetica-Bold",
                                     fontSize=8.4, textColor=colors.HexColor(ACCENT),
                                     leading=12, alignment=2),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=8.8,
                                  textColor=colors.HexColor(INK), leading=12.8,
                                  leftIndent=10, spaceAfter=2),
        "sb_h": ParagraphStyle("sb_h", fontName="Helvetica-Bold", fontSize=9.6,
                                textColor=colors.HexColor(SIDEBAR_TEXT), leading=12,
                                spaceBefore=16, spaceAfter=6),
        "sb_item": ParagraphStyle("sb_item", fontName="Helvetica", fontSize=8.4,
                                   textColor=colors.HexColor(SIDEBAR_DIM), leading=12.5),
    }

    # ---------- page decoration: dark sidebar (page 1 only) ----------
    def draw_sidebar(c, doc):
        c.saveState()
        c.setFillColor(colors.HexColor(SIDEBAR_BG))
        c.rect(0, 0, SB_W, PAGE_H, stroke=0, fill=1)

        pad = 20
        sx = pad
        sw = SB_W - pad * 2
        y = PAGE_H - 34

        # photo (or initials placeholder)
        r = 44
        cx, cy = SB_W / 2, y - r
        if photo_buf is not None:
            c.saveState()
            path = c.beginPath()
            path.circle(cx, cy, r)
            c.clipPath(path, stroke=0, fill=0)
            c.drawImage(ImageReader(photo_buf), cx - r, cy - r,
                        width=r * 2, height=r * 2, mask='auto')
            c.restoreState()
        else:
            initials = "".join([w[0].upper() for w in name.split()[:2]]) or "?"
            c.setFillColor(colors.HexColor(SIDEBAR_LINE))
            c.circle(cx, cy, r, stroke=0, fill=1)
            c.setFillColor(colors.HexColor(SIDEBAR_TEXT))
            c.setFont("Helvetica-Bold", 26)
            c.drawCentredString(cx, cy - 9, initials)
        c.setStrokeColor(colors.HexColor(ACCENT))
        c.setLineWidth(2)
        c.circle(cx, cy, r, stroke=1, fill=0)
        y = cy - r - 22

        # name + title
        c.setFillColor(colors.HexColor(SIDEBAR_TEXT))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(SB_W / 2, y, name)
        y -= 16
        c.setFillColor(colors.HexColor(ACCENT))
        c.setFont("Helvetica-Bold", 8.6)
        c.drawCentredString(SB_W / 2, y, title.upper())
        y -= 20

        def sb_heading(text):
            nonlocal y
            c.setStrokeColor(colors.HexColor(SIDEBAR_LINE))
            c.setLineWidth(1)
            c.line(sx, y, sx + sw, y)
            y -= 14
            c.setFillColor(colors.HexColor(SIDEBAR_TEXT))
            c.setFont("Helvetica-Bold", 9.4)
            c.drawString(sx, y, text.upper())
            y -= 14

        def sb_para(text, gap_after=6, size=8.4):
            nonlocal y
            style = ParagraphStyle("tmp", fontName="Helvetica", fontSize=size,
                                    textColor=colors.HexColor(SIDEBAR_DIM), leading=12)
            p = Paragraph(text, style)
            w, h = p.wrap(sw, 400)
            p.drawOn(c, sx, y - h)
            y -= h + gap_after

        if contact:
            sb_heading("Contact")
            for label, value in contact.items():
                sb_para(f"<b><font color='{SIDEBAR_TEXT}'>{label}</font></b><br/>{value}",
                        gap_after=8)

        if skills:
            sb_heading("Skills")
            for s in skills:
                sb_para(f"&#8226;&nbsp; {s}", gap_after=4)

        if languages:
            sb_heading("Languages")
            for lang, level in languages:
                sb_para(f"<b><font color='{SIDEBAR_TEXT}'>{lang}</font></b> — {level}",
                        gap_after=6)

        if hobbies:
            sb_heading("Hobbies")
            for h in hobbies:
                sb_para(f"&#8226;&nbsp; {h}", gap_after=4)

        c.restoreState()

    def draw_later_page(c, doc):
        c.saveState()
        c.setFillColor(colors.HexColor(DIM))
        c.setFont("Helvetica", 7.5)
        c.drawRightString(PAGE_W - MARGIN, 12, f"{name} — CV (continued)")
        c.restoreState()

    # ---------- frames ----------
    main_frame_1 = Frame(SB_W + MARGIN, MARGIN, PAGE_W - SB_W - MARGIN * 2,
                          PAGE_H - MARGIN * 2, id="main1",
                          leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    main_frame_later = Frame(MARGIN, MARGIN, PAGE_W - MARGIN * 2, PAGE_H - MARGIN * 2,
                              id="main_later", leftPadding=0, rightPadding=0,
                              topPadding=0, bottomPadding=0)

    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4, title=f"{name} — CV")
    doc.addPageTemplates([
        PageTemplate(id="Page1", frames=[main_frame_1], onPage=draw_sidebar),
        PageTemplate(id="Later", frames=[main_frame_later], onPage=draw_later_page),
    ])

    def section_heading(text):
        return Paragraph(text.upper(), styles["h2"])

    def two_col_row(left_flowable, right_text, right_style="item_date"):
        row = Table([[left_flowable, Paragraph(right_text, styles[right_style])]],
                    colWidths=["*", 110])
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return row

    story = [NextPageTemplate("Later")]

    if profile:
        story.append(section_heading("Profile"))
        story.append(Paragraph(profile, styles["body"]))

    if experience:
        story.append(section_heading("Work Experience"))
        for entry in experience:
            block = [two_col_row(Paragraph(entry["role"], styles["item_title"]),
                                  entry.get("duration", ""))]
            if entry.get("company"):
                block.append(Paragraph(entry["company"], styles["item_sub"]))
            for b in entry.get("bullets", []):
                block.append(Paragraph(f"&#8226;&nbsp; {b}", styles["bullet"]))
            block.append(Spacer(1, 10))
            story.append(KeepTogether(block))

    if education:
        story.append(section_heading("Education"))
        for edu in education:
            block = [two_col_row(Paragraph(edu["degree"], styles["item_title"]),
                                  edu.get("duration", ""))]
            if edu.get("institution"):
                block.append(Paragraph(edu["institution"], styles["item_sub"]))
            block.append(Spacer(1, 10))
            story.append(KeepTogether(block))

    doc.build(story)

    # BaseDocTemplate wrote the PDF into our BytesIO buffer. Rewind it
    # so the caller can read it.
    buf.seek(0)

    # Generate a safe download filename.
    safe_name = (data.get("name") or "CV").replace(".", "").replace(" ", "-")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c == "-")
    filename = f"{safe_name}-CV.pdf"

    # If an output_path was given (standalone CLI mode), also save to file.
    if output_path:
        with open(output_path, "wb") as f:
            f.write(buf.getvalue())

    return buf, filename


if __name__ == "__main__":
    out_path = "My-CV.pdf"
    buf, fname = build_cv_pdf(CV_DATA, out_path)
    print(f"Done! Saved as: {out_path}")