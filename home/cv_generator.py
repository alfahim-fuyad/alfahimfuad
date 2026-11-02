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

# --- palette (dark navy sidebar + blue accent matching the site) ------
INK = "#0f172a"          # main text (dark slate)
DIM = "#64748b"          # secondary text (gray)
ACCENT = "#2563eb"       # blue accent (matches the site)
ACCENT_LIGHT = "#60a5fa" # lighter accent for sidebar
SIDEBAR_BG = "#0f172a"   # dark navy sidebar
SIDEBAR_TEXT = "#f1f5f9" # bright text on sidebar
SIDEBAR_DIM = "#94a3b8"  # dim text on sidebar
SIDEBAR_LINE = "#1e293b" # divider lines on sidebar
RULE = "#e2e8f0"         # divider lines on main column

SIDEBAR_W = 200           # sidebar width in points (~2.78 inches)


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
      - Django settings (SITE_EMAIL, SITE_FULL_NAME, SITE_TITLE, etc.)
      - sensible defaults matching the real website content when no
        Profile row exists yet

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
             else getattr(settings, "SITE_TITLE",
                           "Data Scientist | ML Engineer | AI Builder"))

    # --- Contact ---
    # Real contact info from the site. Phone and location come from the
    # about page; email + GitHub come from settings.
    contact = {}
    if profile and profile.phone:
        contact["Phone"] = profile.phone
    else:
        contact["Phone"] = "+880 1338-136424"
    contact["Email"] = getattr(settings, "SITE_EMAIL",
                               "md.alfahim.fuyad@gmail.com")
    # GitHub
    gh_user = getattr(settings, "SITE_GITHUB_USERNAME", "alfahim-fuyad")
    contact["GitHub"] = f"github.com/{gh_user}"
    if profile and profile.website:
        contact["Website"] = profile.website
    contact["Address"] = (profile.location if profile and profile.location
                          else "South Banasree, Dhaka, Bangladesh")

    # --- Skills ---
    # Parse from Profile.skills if set; otherwise use the real skills
    # from the home page's Technical Skills section.
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
        skills = [
            # Languages
            "Python", "SQL", "JavaScript", "HTML / CSS",
            # Data Science & ML
            "Pandas", "NumPy", "scikit-learn", "TensorFlow",
            "PyTorch", "Matplotlib", "Seaborn",
            # Web & Backend
            "Django", "FastAPI", "REST APIs", "PostgreSQL", "SQLite",
            # Tools
            "Git & GitHub", "Jupyter", "VS Code", "Linux", "Gunicorn",
        ]

    # --- Languages ---
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

    # --- Interests ---
    hobbies = []
    if profile and profile.interests:
        for line in profile.interests.replace(",", "\n").splitlines():
            h = line.strip()
            if h:
                hobbies.append(h)
    if not hobbies:
        hobbies = ["AI Research", "Open Source", "Chess", "Photography"]

    # --- Profile summary ---
    # From the hero section on the home page.
    profile_text = (profile.summary if profile and profile.summary
                    else ("I build intelligent systems — from end-to-end "
                          "data pipelines and predictive models to clean, "
                          "modern web applications powered by AI. "
                          "Currently studying Computer Science at East West "
                          "University, Dhaka, and turning ideas into "
                          "data-driven products."))

    # --- Experience ---
    # Parse from Profile.experience if set (blocks separated by blank
    # lines; first line "Role | Organization | Date range").
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
    if not experience:
        experience = [
            {
                "role": "AI/ML Engineer (Freelance)",
                "company": "Remote",
                "duration": "Jan 2024 – Present",
                "bullets": [
                    "Built and deployed end-to-end ML models and data "
                    "pipelines for clients across healthcare and finance.",
                    "Shipped 5+ production models serving real users, with "
                    "monitoring and CI/CD via GitHub Actions.",
                    "Developed clean, responsive web applications with "
                    "Django and REST APIs to serve model predictions.",
                ],
            },
            {
                "role": "Data Science Intern",
                "company": "ABC Tech Solutions, Dhaka",
                "duration": "Jul 2023 – Dec 2023",
                "bullets": [
                    "Analyzed large datasets to extract actionable insights "
                    "and presented findings to stakeholders.",
                    "Built dashboards for real-time KPI monitoring using "
                    "Pandas, Matplotlib, and Seaborn.",
                ],
            },
        ]

    # --- Education ---
    # From about.Education model if set; otherwise the real education
    # journey shown on the About page.
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
                "duration": "2022 – Present",
            },
            {
                "degree": "Higher Secondary Certificate (HSC)",
                "institution": "Agricultural University College, Mymensingh",
                "duration": "2019 – 2021",
            },
            {
                "degree": "Secondary School Certificate (SSC)",
                "institution": "Anjuman Adarsha Govt. High School, Netrakona",
                "duration": "2017 – 2019",
            },
        ]

    # --- Certifications ---
    certifications = []
    if profile and profile.certifications:
        for line in profile.certifications.splitlines():
            c = line.strip()
            if c:
                certifications.append(c)

    # --- Achievements / awards ---
    achievements = []
    if profile and profile.achievements:
        for line in profile.achievements.splitlines():
            a = line.strip()
            if a:
                achievements.append(a)

    # --- Photo ---
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
        "certifications": certifications,
        "achievements": achievements,
    }


def build_cv_pdf(data, output_path=None):
    """Build a clean, professional CV PDF matching the reference layout.

    Layout: two-column A4 page.
      - Left sidebar (dark navy, ~200pt wide): photo, name, title,
        contact, skills, languages, certifications, achievements.
      - Right main column (white): profile summary, work experience,
        education.

    Parameters:
        data         dict from build_cv_data()
        output_path  optional filename — if given, the PDF is ALSO saved
                     to that file (standalone CLI mode).

    Returns:
        (buffer, filename) — BytesIO positioned at 0 + safe filename.
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
    MARGIN = 14 * mm
    SB_W = SIDEBAR_W
    MAIN_X = SB_W + MARGIN
    MAIN_W = PAGE_W - SB_W - MARGIN * 2

    name = data.get("name", "Your Name")
    title = data.get("title", "")
    contact = data.get("contact", {})
    skills = data.get("skills", [])
    languages = data.get("languages", [])
    hobbies = data.get("hobbies", [])
    profile_text = data.get("profile", "")
    experience = data.get("experience", [])
    education = data.get("education", [])
    certifications = data.get("certifications", [])
    achievements = data.get("achievements", [])

    photo_buf = _circular_photo(data.get("photo"))

    # ---------- paragraph styles ----------
    # Main column styles (on white)
    s_h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=11,
                          textColor=colors.HexColor(ACCENT), leading=14,
                          spaceBefore=4, spaceAfter=2)
    s_h1_rule_after = 2  # mm of rule below h1
    s_body = ParagraphStyle("body", fontName="Helvetica", fontSize=9.3,
                            leading=13.5, textColor=colors.HexColor(INK))
    s_role = ParagraphStyle("role", fontName="Helvetica-Bold", fontSize=10.5,
                            textColor=colors.HexColor(INK), leading=13)
    s_company = ParagraphStyle("company", fontName="Helvetica",
                               fontSize=9, textColor=colors.HexColor(DIM),
                               leading=12)
    s_date = ParagraphStyle("date", fontName="Helvetica-Bold", fontSize=8.5,
                            textColor=colors.HexColor(ACCENT), leading=12,
                            alignment=2)  # right
    s_bullet = ParagraphStyle("bullet", fontName="Helvetica", fontSize=9,
                              textColor=colors.HexColor(INK), leading=12.5,
                              leftIndent=8, bulletIndent=0, spaceAfter=1)
    s_edu_degree = ParagraphStyle("edu_degree", fontName="Helvetica-Bold",
                                  fontSize=10, textColor=colors.HexColor(INK),
                                  leading=13)
    s_edu_inst = ParagraphStyle("edu_inst", fontName="Helvetica",
                                fontSize=9, textColor=colors.HexColor(DIM),
                                leading=12)

    # Sidebar styles (on dark navy)
    sb_name = ParagraphStyle("sb_name", fontName="Helvetica-Bold", fontSize=14,
                             textColor=colors.HexColor(SIDEBAR_TEXT),
                             leading=17, alignment=1, spaceAfter=1)
    sb_title = ParagraphStyle("sb_title", fontName="Helvetica", fontSize=8.5,
                              textColor=colors.HexColor(ACCENT_LIGHT),
                              leading=11, alignment=1, spaceAfter=2)
    sb_h = ParagraphStyle("sb_h", fontName="Helvetica-Bold", fontSize=9.5,
                          textColor=colors.HexColor(SIDEBAR_TEXT), leading=12,
                          spaceBefore=10, spaceAfter=3)
    sb_label = ParagraphStyle("sb_label", fontName="Helvetica-Bold", fontSize=8,
                              textColor=colors.HexColor(ACCENT_LIGHT),
                              leading=11, spaceAfter=0)
    sb_val = ParagraphStyle("sb_val", fontName="Helvetica", fontSize=8.2,
                            textColor=colors.HexColor(SIDEBAR_DIM),
                            leading=11.5, spaceAfter=5)
    sb_item = ParagraphStyle("sb_item", fontName="Helvetica", fontSize=8.4,
                             textColor=colors.HexColor(SIDEBAR_DIM),
                             leading=12, spaceAfter=2)
    sb_lang = ParagraphStyle("sb_lang", fontName="Helvetica", fontSize=8.4,
                             textColor=colors.HexColor(SIDEBAR_DIM),
                             leading=12, spaceAfter=4)

    # ---------- page decoration ----------
    def draw_sidebar(c, doc):
        """Draw the dark sidebar background + photo + name/title."""
        c.saveState()
        # Full-height dark sidebar
        c.setFillColor(colors.HexColor(SIDEBAR_BG))
        c.rect(0, 0, SB_W, PAGE_H, stroke=0, fill=1)

        pad = 18
        y = PAGE_H - pad

        # Photo (circular) or initials placeholder
        r = 42
        cx = SB_W / 2
        cy = y - r
        if photo_buf is not None:
            c.saveState()
            clip_path = c.beginPath()
            clip_path.circle(cx, cy, r)
            c.clipPath(clip_path, stroke=0, fill=0)
            c.drawImage(ImageReader(photo_buf), cx - r, cy - r,
                        width=r * 2, height=r * 2, mask='auto')
            c.restoreState()
        else:
            initials = "".join([w[0].upper() for w in name.split()[:2]]) or "?"
            c.setFillColor(colors.HexColor(SIDEBAR_LINE))
            c.circle(cx, cy, r, stroke=0, fill=1)
            c.setFillColor(colors.HexColor(SIDEBAR_TEXT))
            c.setFont("Helvetica-Bold", 22)
            c.drawCentredString(cx, cy - 8, initials)
        # Thin accent ring around the photo
        c.setStrokeColor(colors.HexColor(ACCENT))
        c.setLineWidth(1.5)
        c.circle(cx, cy, r + 2, stroke=1, fill=0)

        y = cy - r - 12

        # Name + title on the sidebar
        c.setFillColor(colors.HexColor(SIDEBAR_TEXT))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(cx, y, name)
        y -= 14
        if title:
            c.setFillColor(colors.HexColor(ACCENT_LIGHT))
            c.setFont("Helvetica", 8.5)
            # Word-wrap the title manually (centered)
            for line in _wrap_text(title, "Helvetica", 8.5, SB_W - pad * 2):
                c.drawCentredString(cx, y, line)
                y -= 10

        c.restoreState()

    def draw_main_bg(c, doc):
        """Draw the section heading rules on the main column — actually
        we let the story flowables handle the rules, so this is a no-op
        for the main column background (white by default)."""
        pass

    def draw_later_page(c, doc):
        """Continuation pages: just the sidebar, no photo/name."""
        c.saveState()
        c.setFillColor(colors.HexColor(SIDEBAR_BG))
        c.rect(0, 0, SB_W, PAGE_H, stroke=0, fill=1)
        # Footer on main column
        c.setFillColor(colors.HexColor(DIM))
        c.setFont("Helvetica", 7.5)
        c.drawRightString(PAGE_W - MARGIN, 12,
                          f"{name} — CV (continued)")
        c.restoreState()

    # ---------- frames ----------
    # Sidebar frame (only for the sidebar content flowables — the photo
    # and name are drawn directly on the canvas in draw_sidebar).
    sb_frame = Frame(
        18, 60, SB_W - 36, PAGE_H - 60 - 200,
        id="sidebar",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        showBoundary=0,
    )
    # Main column frame (page 1) — starts below the top margin, to the
    # right of the sidebar.
    main_frame_1 = Frame(
        MAIN_X, MARGIN, MAIN_W, PAGE_H - MARGIN * 2 - 8,
        id="main1",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    # Main column frame (later pages) — full width minus margins.
    main_frame_later = Frame(
        MARGIN, MARGIN + 14, PAGE_W - MARGIN * 2, PAGE_H - MARGIN * 2 - 14,
        id="main_later",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )

    buf = io.BytesIO()
    doc = BaseDocTemplate(buf, pagesize=A4,
                          title=f"{name} — CV",
                          author=name,
                          subject="Curriculum Vitae")
    doc.addPageTemplates([
        PageTemplate(id="Page1", frames=[sb_frame, main_frame_1],
                     onPage=draw_sidebar),
        PageTemplate(id="Later", frames=[main_frame_later],
                     onPage=draw_later_page),
    ])

    # ---------- helpers ----------
    def section_heading(text):
        """A section heading with a thin rule underneath."""
        return Table(
            [[Paragraph(text.upper(), s_h1)],
             [_thin_rule(MAIN_W, colors.HexColor(RULE), 0.6)]],
            colWidths=[MAIN_W],
            style=TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (0, 0), 1),
                ("BOTTOMPADDING", (0, 1), (0, 1), 8),
                ("LINEBELOW", (0, 0), (0, 0), 0, colors.transparent),
            ]),
        )

    def sb_section_heading(text):
        """Sidebar section heading with a small accent line."""
        return Table(
            [[Paragraph(text.upper(), sb_h)],
             [_thin_rule(SB_W - 36, colors.HexColor(ACCENT), 1)]],
            colWidths=[SB_W - 36],
            style=TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (0, 0), 2),
                ("BOTTOMPADDING", (0, 1), (0, 1), 6),
            ]),
        )

    def two_col_row(left_flowable, right_text):
        """A two-column row: left = flowable, right = right-aligned text."""
        row = Table(
            [[left_flowable, Paragraph(right_text, s_date)]],
            colWidths=[MAIN_W - 90, 90],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]),
        )
        return row

    # ---------- build the sidebar story ----------
    sb_story = []
    if contact:
        sb_story.append(sb_section_heading("Contact"))
        for label, value in contact.items():
            sb_story.append(Paragraph(label.upper(), sb_label))
            sb_story.append(Paragraph(value, sb_val))
    if skills:
        sb_story.append(sb_section_heading("Skills"))
        for s in skills:
            sb_story.append(Paragraph(f"&#8226;&nbsp; {s}", sb_item))
    if languages:
        sb_story.append(sb_section_heading("Languages"))
        for lang, level in languages:
            sb_story.append(Paragraph(
                f"<b><font color='{SIDEBAR_TEXT}'>{lang}</font></b>"
                + (f" — {level}" if level else ""),
                sb_lang))
    if certifications:
        sb_story.append(sb_section_heading("Certifications"))
        for c in certifications:
            sb_story.append(Paragraph(f"&#8226;&nbsp; {c}", sb_item))
    if achievements:
        sb_story.append(sb_section_heading("Awards"))
        for a in achievements:
            sb_story.append(Paragraph(f"&#8226;&nbsp; {a}", sb_item))
    if hobbies:
        sb_story.append(sb_section_heading("Interests"))
        for h in hobbies:
            sb_story.append(Paragraph(f"&#8226;&nbsp; {h}", sb_item))

    # ---------- build the main story ----------
    story = []
    # Start on Page1 (which has both sidebar + main frames).
    # The sidebar story goes into the sidebar frame; the main story
    # goes into the main frame. ReportLab fills frames in the order
    # they appear in the PageTemplate's frames list.
    # We need to tell the story which frame to use.

    # Sidebar content first (goes into sb_frame).
    story.extend(sb_story)

    # Force the next content into the main frame.
    from reportlab.platypus import FrameBreak
    story.append(FrameBreak())

    if profile_text:
        story.append(section_heading("Profile"))
        story.append(Paragraph(profile_text, s_body))
        story.append(Spacer(1, 6))

    if experience:
        story.append(section_heading("Work Experience"))
        for entry in experience:
            block = [two_col_row(
                Paragraph(entry["role"], s_role),
                entry.get("duration", ""))]
            if entry.get("company"):
                block.append(Paragraph(entry["company"], s_company))
            block.append(Spacer(1, 2))
            for b in entry.get("bullets", []):
                block.append(Paragraph(
                    f"&#8226;&nbsp; {b}", s_bullet))
            block.append(Spacer(1, 8))
            story.append(KeepTogether(block))

    if education:
        story.append(section_heading("Education"))
        for edu in education:
            block = [two_col_row(
                Paragraph(edu["degree"], s_edu_degree),
                edu.get("duration", ""))]
            if edu.get("institution"):
                block.append(Paragraph(edu["institution"], s_edu_inst))
            block.append(Spacer(1, 8))
            story.append(KeepTogether(block))

    # Switch to the "Later" template for any overflow.
    story.append(NextPageTemplate("Later"))

    doc.build(story)

    buf.seek(0)

    # Generate a safe download filename.
    safe_name = (data.get("name") or "CV").replace(".", "").replace(" ", "-")
    safe_name = "".join(c for c in safe_name if c.isalnum() or c == "-")
    filename = f"{safe_name}-CV.pdf"

    if output_path:
        with open(output_path, "wb") as f:
            f.write(buf.getvalue())

    return buf, filename


# --- small helpers used by build_cv_pdf ---

def _thin_rule(width, color, thickness=0.5):
    """Return a thin horizontal rule as a flowable (a 1-cell Table)."""
    from reportlab.platypus import Table, TableStyle
    t = Table([[""]], colWidths=[width], rowHeights=[thickness])
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (0, 0), thickness, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def _wrap_text(text, font, size, max_width):
    """Simple word-wrap that returns a list of lines fitting within max_width."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    words = text.split()
    if not words:
        return []
    lines = []
    current = words[0]
    for w in words[1:]:
        test = current + " " + w
        if stringWidth(test, font, size) <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines


if __name__ == "__main__":
    out_path = "My-CV.pdf"
    buf, fname = build_cv_pdf(CV_DATA, out_path)
    print(f"Done! Saved as: {out_path}")
