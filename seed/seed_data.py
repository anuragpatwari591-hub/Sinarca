"""
Seed script — populates NAVORA with a representative content set (spec section 42)
and the Demo Student / Admin accounts (spec section 50).

Run with:  python -m seed.seed_data
Safe to re-run: it upserts by unique slug/email instead of duplicating rows.

Resource metadata (title, provider, URL) points to real, publicly available,
free-to-link educational sources. No ratings are fabricated: every seeded
resource's rating is left as "unavailable" unless explicitly noted, and the
two paid course examples carry an "indicative price — verify on provider
site" note rather than a fabricated precise figure.
"""

import os
from datetime import datetime, date, timedelta

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models import (
    Stream, Skill, Career, Resource, Roadmap, RoadmapStage, RoadmapResource,
    Project, User, EducationProfile, LearningDNA, UserSkill, UserRoadmapProgress,
    LearningProgress, StudySession, Bookmark, UserProject,
)


def get_or_create(model, defaults=None, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False
    params = dict(kwargs)
    params.update(defaults or {})
    instance = model(**params)
    db.session.add(instance)
    db.session.flush()
    return instance, True


# ---------------------------------------------------------------------------
# Streams
# ---------------------------------------------------------------------------

STREAMS = [
    ("B.Tech", "b-tech", "technology"),
    ("B.E.", "be", "technology"),
    ("BCA", "bca", "technology"),
    ("MCA", "mca", "technology"),
    ("BBA", "bba", "management"),
    ("MBA", "mba", "management"),
    ("B.Com", "b-com", "commerce"),
    ("M.Com", "m-com", "commerce"),
    ("CA", "ca", "professional"),
    ("CS", "cs-company-secretary", "professional"),
    ("CMA", "cma", "professional"),
    ("BA", "ba", "arts"),
    ("MA", "ma", "arts"),
    ("B.Sc", "b-sc", "science"),
    ("M.Sc", "m-sc", "science"),
    ("Law", "law", "law"),
    ("Design", "design", "design"),
    ("Pharmacy", "pharmacy", "science"),
]


def seed_streams():
    for name, slug, category in STREAMS:
        get_or_create(Stream, slug=slug, defaults={"name": name, "category": category})
    db.session.commit()
    print(f"Streams: {Stream.query.count()}")


# ---------------------------------------------------------------------------
# Skills (with prerequisite chains)
# ---------------------------------------------------------------------------

SKILLS = [
    ("Python", "python", "programming", None),
    ("Git & GitHub", "git", "programming", None),
    ("HTML & CSS", "html-css", "programming", None),
    ("JavaScript", "javascript", "programming", "html-css"),
    ("Data Structures", "data-structures", "programming", "python"),
    ("SQL", "sql", "data", None),
    ("Data Analysis", "data-analysis", "data", "sql"),
    ("Business Analytics", "business-analytics", "data", "sql"),
    ("Networking", "networking", "security", None),
    ("Linux", "linux", "security", None),
    ("Security Fundamentals", "security-fundamentals", "security", "networking"),
    ("Web Security", "web-security", "security", "security-fundamentals"),
    ("AI Fundamentals", "ai-fundamentals", "ai", "python"),
    ("Machine Learning", "machine-learning", "ai", "ai-fundamentals"),
    ("Accounting Basics", "accounting-basics", "finance", None),
    ("Financial Management", "financial-management", "finance", "accounting-basics"),
    ("Taxation", "taxation", "finance", "accounting-basics"),
    ("Business Law", "business-law", "finance", None),
    ("Marketing Fundamentals", "marketing-fundamentals", "marketing", None),
    ("Digital Marketing", "digital-marketing", "marketing", "marketing-fundamentals"),
    ("HR Management", "hr-management", "management", None),
    ("Operations Management", "operations-management", "management", None),
    ("UI/UX Design", "ui-ux-design", "design", None),
    ("Graphic Design", "graphic-design", "design", None),
    ("Aptitude & Reasoning", "aptitude-reasoning", "aptitude", None),
]


def seed_skills():
    for name, slug, category, _ in SKILLS:
        get_or_create(Skill, slug=slug, defaults={"name": name, "category": category})
    db.session.commit()

    for name, slug, category, prereq_slug in SKILLS:
        if prereq_slug:
            skill = Skill.query.filter_by(slug=slug).first()
            prereq = Skill.query.filter_by(slug=prereq_slug).first()
            skill.prerequisite_skill_id = prereq.id
    db.session.commit()
    print(f"Skills: {Skill.query.count()}")


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

def R(title, provider, url, category, topic, tags, difficulty, minutes, resource_type,
      free=True, price=0, fmt=None, desc="", prereq="", language="English", verified_days_ago=10,
      affiliate=None, sponsored=False, rating_note=None):
    return dict(
        title=title, provider=provider, url=url, category=category, topic=topic,
        skill_tags=tags, difficulty=difficulty, duration_minutes=minutes,
        resource_type=resource_type, is_free=free, price_inr=price,
        format_tags=fmt or [], description=desc, prerequisites=prereq, language=language,
        last_verified_at=datetime.utcnow() - timedelta(days=verified_days_ago),
        affiliate_url=affiliate, is_sponsored=sponsored,
        rating=None, rating_count=None, rating_source=None,
    )


RESOURCES = [
    R("The Python Tutorial", "Python Software Foundation", "https://docs.python.org/3/tutorial/",
      "technology", "Python", ["python"], "beginner", 300, "docs",
      fmt=["reading", "practice-first"],
      desc="The official Python tutorial — the most authoritative free introduction to the language."),

    R("Scientific Computing with Python", "freeCodeCamp", "https://www.freecodecamp.org/learn/scientific-computing-with-python/",
      "technology", "Python", ["python"], "beginner", 900, "course",
      fmt=["project-first", "interactive"],
      desc="A free, project-based certification covering Python fundamentals through five projects."),

    R("Version Control with Git", "GitHub Docs", "https://docs.github.com/en/get-started/using-git/about-git",
      "technology", "Git & GitHub", ["git"], "beginner", 60, "docs",
      fmt=["reading"], desc="Official GitHub documentation on how Git and version control work."),

    R("Learn HTML & CSS", "MDN Web Docs", "https://developer.mozilla.org/en-US/docs/Learn/HTML",
      "technology", "Web Development", ["html-css"], "beginner", 480, "docs",
      fmt=["reading", "practice-first"], desc="Mozilla's structured, free curriculum for HTML and CSS fundamentals."),

    R("JavaScript Guide", "MDN Web Docs", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
      "technology", "Web Development", ["javascript"], "intermediate", 420, "docs",
      fmt=["reading"], desc="The definitive free guide to JavaScript from Mozilla.", prereq="HTML & CSS"),

    R("Data Structures Tutorial", "GeeksforGeeks", "https://www.geeksforgeeks.org/data-structures/",
      "technology", "Data Structures", ["data-structures"], "intermediate", 600, "article",
      fmt=["reading", "practice-first"], desc="A comprehensive free reference for core data structures and their implementations.",
      prereq="Python or another programming language"),

    R("SQL Tutorial", "W3Schools", "https://www.w3schools.com/sql/",
      "technology", "SQL", ["sql"], "beginner", 240, "docs",
      fmt=["reading", "practice-first"], desc="A free, example-driven reference for SQL syntax and queries."),

    R("SQL Practice: Learn SQL", "SQLBolt", "https://sqlbolt.com/",
      "technology", "SQL", ["sql"], "beginner", 180, "practice",
      fmt=["interactive", "practice-first"], desc="Free interactive SQL exercises that run in the browser."),

    R("Kaggle Learn: Pandas", "Kaggle", "https://www.kaggle.com/learn/pandas",
      "technology", "Data Analysis", ["data-analysis", "sql"], "intermediate", 240, "course",
      fmt=["interactive", "project-first"], desc="A free, hands-on micro-course on data manipulation with pandas.",
      prereq="Python basics"),

    R("Kaggle Learn: Intro to SQL", "Kaggle", "https://www.kaggle.com/learn/intro-to-sql",
      "technology", "Data Analysis", ["sql", "data-analysis"], "beginner", 180, "course",
      fmt=["interactive", "project-first"], desc="A free hands-on introduction to SQL for data analysis using BigQuery."),

    R("Networking Basics", "Cisco Networking Academy", "https://www.netacad.com/courses/networking",
      "technology", "Networking", ["networking"], "beginner", 900, "course",
      fmt=["video", "long-form"], desc="Cisco's free introductory networking curriculum covering the fundamentals of how networks work."),

    R("Linux Journey", "Linux Journey", "https://linuxjourney.com/",
      "technology", "Linux", ["linux"], "beginner", 420, "interactive",
      fmt=["interactive", "short-tutorials"], desc="A free, friendly, self-paced introduction to the Linux command line and system administration."),

    R("OWASP Top 10", "OWASP Foundation", "https://owasp.org/www-project-top-ten/",
      "technology", "Web Security", ["web-security", "security-fundamentals"], "intermediate", 180, "docs",
      fmt=["reading"], desc="The industry-standard, free reference for the ten most critical web application security risks.",
      prereq="Networking fundamentals"),

    R("Introduction to Cybersecurity", "Cisco Networking Academy", "https://www.netacad.com/courses/cybersecurity/introduction-cybersecurity",
      "technology", "Security Fundamentals", ["security-fundamentals", "networking"], "beginner", 360, "course",
      fmt=["video", "short-tutorials"], desc="A free introductory course covering core cybersecurity concepts and career paths."),

    R("CS50's Introduction to Artificial Intelligence", "Harvard (edX/CS50)", "https://cs50.harvard.edu/ai/",
      "technology", "AI Fundamentals", ["ai-fundamentals", "python"], "advanced", 1800, "course",
      fmt=["video", "long-form", "project-first"], desc="Harvard's free, project-based introduction to AI concepts and algorithms using Python.",
      prereq="Python"),

    R("Machine Learning Crash Course", "Google Developers", "https://developers.google.com/machine-learning/crash-course",
      "technology", "Machine Learning", ["machine-learning", "ai-fundamentals"], "advanced", 900, "course",
      fmt=["video", "interactive"], desc="Google's free, practical crash course on machine learning concepts and TensorFlow."),

    R("Core Finance", "Khan Academy", "https://www.khanacademy.org/economics-finance-domain/core-finance",
      "commerce", "Accounting Basics", ["accounting-basics"], "beginner", 600, "video",
      fmt=["video", "short-tutorials"], desc="Khan Academy's free video series covering accounting and core finance concepts."),

    R("Financial Management Basics", "Khan Academy", "https://www.khanacademy.org/economics-finance-domain/core-finance/investment-vehicles-tutorial",
      "commerce", "Financial Management", ["financial-management", "accounting-basics"], "intermediate", 420, "video",
      fmt=["video"], desc="Free lessons on investment vehicles and financial management fundamentals.",
      prereq="Accounting Basics"),

    R("Income Tax Basics (India)", "Income Tax Department, Govt. of India", "https://incometaxindia.gov.in/",
      "commerce", "Taxation", ["taxation", "accounting-basics"], "intermediate", 240, "docs",
      fmt=["reading"], desc="Official Government of India resource for understanding personal and corporate income tax.",
      prereq="Accounting Basics", language="English"),

    R("Business Law Basics", "Khan Academy", "https://www.khanacademy.org/economics-finance-domain",
      "commerce", "Business Law", ["business-law"], "beginner", 300, "video",
      fmt=["video"], desc="Introductory free content touching on business, economics and legal fundamentals."),

    R("Fundamentals of Digital Marketing", "Google Digital Garage", "https://learndigital.withgoogle.com/digitalgarage",
      "management", "Marketing", ["marketing-fundamentals", "digital-marketing"], "beginner", 2600, "course",
      fmt=["video", "short-tutorials"], desc="Google's free, certified course covering the fundamentals of digital marketing."),

    R("HubSpot Academy: Digital Marketing", "HubSpot Academy", "https://academy.hubspot.com/courses/digital-marketing",
      "management", "Marketing", ["digital-marketing", "marketing-fundamentals"], "intermediate", 360, "course",
      fmt=["video"], desc="A free certified course on digital marketing strategy from HubSpot Academy.",
      prereq="Marketing Fundamentals"),

    R("Introduction to Operations Management", "MIT OpenCourseWare", "https://ocw.mit.edu/courses/15-760j-fundamentals-of-manufacturing-systems-fall-2005/",
      "management", "Operations", ["operations-management"], "advanced", 900, "course",
      fmt=["reading", "long-form"], desc="Free MIT OpenCourseWare materials on manufacturing and operations systems fundamentals."),

    R("Introduction to HR Management", "Alison", "https://alison.com/tag/human-resource-management",
      "management", "HR", ["hr-management"], "beginner", 300, "course",
      fmt=["video"], desc="Free introductory human resource management courses."),

    R("Foundations of User Experience (UX) Design", "Google Career Certificates (YouTube)", "https://www.youtube.com/c/GoogleCareerCertificates",
      "design", "UI/UX Design", ["ui-ux-design"], "beginner", 480, "video",
      fmt=["video", "short-tutorials"], desc="Free introductory UX design videos from Google's career certificate program."),

    R("Graphic Design Basics", "Canva Design School", "https://www.canva.com/learn/design-school/",
      "design", "Graphic Design", ["graphic-design"], "beginner", 240, "article",
      fmt=["reading", "visual"], desc="Free, visual design fundamentals lessons from Canva's Design School."),

    R("Aptitude Practice", "IndiaBIX", "https://www.indiabix.com/aptitude/questions-and-answers/",
      "professional", "Aptitude", ["aptitude-reasoning"], "beginner", 180, "practice",
      fmt=["practice-first"], desc="Free practice questions for quantitative aptitude and logical reasoning, useful for placements and government exams."),

    # --- Paid examples (spec section 15) — indicative pricing, clearly noted ---
    R("Google Data Analytics Professional Certificate", "Coursera", "https://www.coursera.org/professional-certificates/google-data-analytics",
      "technology", "Data Analysis", ["data-analysis", "sql"], "beginner", 7200, "course",
      free=False, price=1999,
      fmt=["video", "project-first"],
      desc="A structured, certificate-bearing program covering the full data analytics workflow. "
           "Price shown is an indicative monthly-subscription estimate — verify current pricing on Coursera.",
      prereq="None"),

    R("100 Days of Code: The Complete Python Pro Bootcamp", "Udemy", "https://www.udemy.com/course/100-days-of-code/",
      "technology", "Python", ["python", "data-structures"], "beginner", 6000, "course",
      free=False, price=649,
      fmt=["video", "project-first"],
      desc="A long-form, project-heavy Python bootcamp. Price shown is an indicative discounted-Udemy estimate — "
           "verify current pricing on Udemy.",
      prereq="None"),
]


def seed_resources():
    for r in RESOURCES:
        get_or_create(Resource, url=r["url"], defaults=r)
    db.session.commit()
    print(f"Resources: {Resource.query.count()}")


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

PROJECTS = [
    dict(title="Command-Line Calculator", difficulty="beginner", estimated_hours=3,
         description="A calculator that runs in the terminal and supports the four basic operations plus error handling.",
         required_skills=["python"], technologies=["Python"],
         learning_outcomes=["Functions and control flow", "Input validation", "Basic error handling"],
         github_checklist=["README with usage instructions", "Unit tests for each operation", "requirements.txt"],
         portfolio_description="A simple CLI calculator demonstrating clean function design and input validation."),

    dict(title="Personal Expense Tracker", difficulty="beginner", estimated_hours=6,
         description="Track daily expenses in a local SQLite database with category summaries.",
         required_skills=["python", "sql"], technologies=["Python", "SQLite"],
         learning_outcomes=["CRUD with SQL", "Basic data aggregation", "File/database persistence"],
         github_checklist=["Schema diagram in README", "Sample data seed script", "Basic tests"],
         portfolio_description="A CLI/GUI expense tracker showing practical SQL and Python integration."),

    dict(title="Quiz Application", difficulty="beginner", estimated_hours=5,
         description="A multiple-choice quiz app with score tracking and a review of wrong answers.",
         required_skills=["python"], technologies=["Python"],
         learning_outcomes=["Data structures for question banks", "Scoring logic", "User input handling"],
         github_checklist=["At least 20 sample questions", "README with rules", "Tests for scoring logic"],
         portfolio_description="An interactive quiz app demonstrating clean state management."),

    dict(title="Personal Portfolio Website", difficulty="beginner", estimated_hours=8,
         description="A responsive personal portfolio site built with semantic HTML and CSS.",
         required_skills=["html-css"], technologies=["HTML", "CSS"],
         learning_outcomes=["Responsive layout", "Semantic HTML", "Basic accessibility"],
         github_checklist=["Deployed live link in README", "Mobile-responsive check", "Lighthouse accessibility pass"],
         portfolio_description="A live, responsive personal site — often the first thing recruiters see."),

    dict(title="Blog REST API", difficulty="intermediate", estimated_hours=14,
         description="A REST API for creating, reading, updating and deleting blog posts with basic auth.",
         required_skills=["python", "sql", "data-structures"], technologies=["Python", "Flask", "SQLite"],
         learning_outcomes=["REST API design", "Authentication basics", "Database modeling"],
         github_checklist=["API documentation (endpoints + examples)", "Postman/curl examples", "Basic tests"],
         portfolio_description="A documented REST API demonstrating backend fundamentals."),

    dict(title="Sales Data Analysis Dashboard", difficulty="intermediate", estimated_hours=12,
         description="Analyze a public sales dataset and present insights with charts.",
         required_skills=["python", "sql", "data-analysis"], technologies=["Python", "pandas", "SQL"],
         learning_outcomes=["Data cleaning", "Aggregation and grouping", "Basic visualization"],
         github_checklist=["Dataset source cited", "Notebook or dashboard link", "Summary of insights"],
         portfolio_description="A data analysis project showing the full workflow from raw data to insight."),

    dict(title="Network Port Scanner", difficulty="intermediate", estimated_hours=10,
         description="A Python tool that scans a local network range for open ports (for learning/lab use only).",
         required_skills=["python", "networking"], technologies=["Python", "sockets"],
         learning_outcomes=["Socket programming", "Networking fundamentals in practice", "Ethical scanning boundaries"],
         github_checklist=["Clear disclaimer: lab/authorized use only", "README with usage", "Basic tests"],
         portfolio_description="A defensive-security-themed networking project, built and used only on your own lab network."),

    dict(title="Secure Login System", difficulty="advanced", estimated_hours=16,
         description="A login system implementing password hashing, session handling and OWASP Top 10 mitigations.",
         required_skills=["python", "web-security", "security-fundamentals"], technologies=["Python", "Flask"],
         learning_outcomes=["Password hashing", "Session security", "Common vulnerability mitigation"],
         github_checklist=["Threat model in README", "Mitigations mapped to OWASP Top 10", "Basic security tests"],
         portfolio_description="A security-focused login system demonstrating applied secure coding practices."),

    dict(title="Job Board Web App", difficulty="advanced", estimated_hours=25,
         description="A full-stack job board with listings, search/filter, and an admin panel.",
         required_skills=["python", "javascript", "sql", "data-structures"], technologies=["Python", "Flask", "JavaScript", "SQL"],
         learning_outcomes=["Full-stack architecture", "Search and filtering", "Admin CRUD flows"],
         github_checklist=["Deployed demo link", "Architecture diagram", "Tests for core flows"],
         portfolio_description="A capstone full-stack project suitable for a placement portfolio."),

    dict(title="Digital Marketing Campaign Case Study", difficulty="intermediate", estimated_hours=10,
         description="Plan and document a mock digital marketing campaign for a small business, including channel strategy and a sample budget.",
         required_skills=["marketing-fundamentals", "digital-marketing"], technologies=["Google Analytics (demo)", "Canva"],
         learning_outcomes=["Channel strategy", "Budget planning", "Basic campaign analytics literacy"],
         github_checklist=["Written case study document", "Sample creative assets", "Mock analytics summary"],
         portfolio_description="A marketing case study demonstrating strategic thinking, useful for BBA/MBA portfolios."),
]


def seed_projects():
    for p in PROJECTS:
        project = Project.query.filter_by(title=p["title"]).first()
        if not project:
            project = Project(
                title=p["title"], difficulty=p["difficulty"], estimated_hours=p["estimated_hours"],
                description=p["description"], portfolio_description=p["portfolio_description"],
            )
            project.required_skills = p["required_skills"]
            project.technologies = p["technologies"]
            project.learning_outcomes = p["learning_outcomes"]
            project.github_checklist = p["github_checklist"]
            db.session.add(project)
    db.session.commit()
    print(f"Projects: {Project.query.count()}")


# ---------------------------------------------------------------------------
# Roadmaps + Careers
# ---------------------------------------------------------------------------

def _resource_by_url(url):
    return Resource.query.filter_by(url=url).first()


def _project_by_title(title):
    return Project.query.filter_by(title=title).first()


def seed_roadmap(slug, title, description, stages):
    roadmap, _ = get_or_create(Roadmap, slug=slug, defaults={"title": title, "description": description})
    if not roadmap.stages:
        for order, (stage_title, stage_desc, hours, resource_urls, milestone_title) in enumerate(stages, start=1):
            stage = RoadmapStage(
                roadmap_id=roadmap.id, order=order, title=stage_title, description=stage_desc,
                estimated_hours=hours,
            )
            if milestone_title:
                proj = _project_by_title(milestone_title)
                if proj:
                    stage.milestone_project_id = proj.id
            db.session.add(stage)
            db.session.flush()
            for i, url in enumerate(resource_urls, start=1):
                res = _resource_by_url(url)
                if res:
                    db.session.add(RoadmapResource(stage_id=stage.id, resource_id=res.id, order=i))
        db.session.commit()
    return roadmap


def seed_careers_and_roadmaps():
    cyber_roadmap = seed_roadmap(
        "cybersecurity-analyst-roadmap", "Cybersecurity Analyst Roadmap",
        "From computer fundamentals to job-ready cybersecurity skills, in nine phases.",
        [
            ("Computer & Networking Fundamentals", "Understand how networks and computers actually work.", 15,
             ["https://www.netacad.com/courses/networking"], None),
            ("Linux", "Get comfortable with the Linux command line — the OS of most security tooling.", 10,
             ["https://linuxjourney.com/"], None),
            ("Python for Security", "Learn Python well enough to write and understand security tooling.", 20,
             ["https://docs.python.org/3/tutorial/", "https://www.freecodecamp.org/learn/scientific-computing-with-python/"],
             "Network Port Scanner"),
            ("Security Fundamentals", "Core security concepts: CIA triad, threats, and defense in depth.", 12,
             ["https://www.netacad.com/courses/cybersecurity/introduction-cybersecurity"], None),
            ("Web Security", "Learn the OWASP Top 10 and how real applications get exploited and defended.", 10,
             ["https://owasp.org/www-project-top-ten/"], "Secure Login System"),
            ("Projects", "Apply what you've learned in defensible, portfolio-ready projects.", 20, [], "Secure Login System"),
            ("Portfolio & Internship Prep", "Package your projects and prepare for interviews.", 8, [], None),
        ],
    )

    data_roadmap = seed_roadmap(
        "data-analyst-roadmap", "Data Analyst Roadmap",
        "From SQL fundamentals to a portfolio-ready data analysis project.",
        [
            ("SQL Fundamentals", "Learn to query and manipulate data with SQL.", 10,
             ["https://www.w3schools.com/sql/", "https://sqlbolt.com/"], None),
            ("Python for Data", "Learn Python and pandas for data manipulation.", 15,
             ["https://www.freecodecamp.org/learn/scientific-computing-with-python/", "https://www.kaggle.com/learn/pandas"],
             None),
            ("Data Analysis in Practice", "Apply SQL + Python to real, messy datasets.", 12,
             ["https://www.kaggle.com/learn/intro-to-sql"], "Sales Data Analysis Dashboard"),
            ("Business Analytics", "Turn analysis into business recommendations.", 8, [], None),
            ("Capstone Project", "Build a complete, documented analysis project for your portfolio.", 15, [],
             "Sales Data Analysis Dashboard"),
        ],
    )

    swe_roadmap = seed_roadmap(
        "software-developer-roadmap", "Software Developer Roadmap",
        "From programming fundamentals to a full-stack capstone project.",
        [
            ("Programming Fundamentals", "Learn Python as your first language.", 15,
             ["https://docs.python.org/3/tutorial/", "https://www.freecodecamp.org/learn/scientific-computing-with-python/"],
             "Command-Line Calculator"),
            ("Git & Collaboration", "Learn version control — essential for every developer.", 4,
             ["https://docs.github.com/en/get-started/using-git/about-git"], None),
            ("Data Structures", "Understand the data structures behind efficient code.", 15,
             ["https://www.geeksforgeeks.org/data-structures/"], None),
            ("Web Development", "Learn HTML, CSS and JavaScript to build for the browser.", 20,
             ["https://developer.mozilla.org/en-US/docs/Learn/HTML", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"],
             "Personal Portfolio Website"),
            ("Backend & APIs", "Learn to build and document REST APIs.", 15, [], "Blog REST API"),
            ("Capstone Project", "Build a full-stack project for your portfolio.", 25, [], "Job Board Web App"),
        ],
    )

    marketing_roadmap = seed_roadmap(
        "digital-marketing-roadmap", "Digital Marketing Manager Roadmap",
        "From marketing fundamentals to running a documented campaign case study.",
        [
            ("Marketing Fundamentals", "Understand the core principles of marketing.", 8,
             ["https://learndigital.withgoogle.com/digitalgarage"], None),
            ("Digital Channels", "Learn SEO, social and paid channels.", 10,
             ["https://academy.hubspot.com/courses/digital-marketing"], None),
            ("Analytics Literacy", "Learn to read and act on campaign data.", 8,
             ["https://www.kaggle.com/learn/intro-to-sql"], None),
            ("Campaign Case Study", "Plan and document a full campaign.", 12, [],
             "Digital Marketing Campaign Case Study"),
        ],
    )

    ca_roadmap = seed_roadmap(
        "chartered-accountant-prep-roadmap", "Chartered Accountancy Foundations Roadmap",
        "Core commerce fundamentals that support CA/CMA/CS preparation alongside your coaching.",
        [
            ("Accounting Basics", "Build a solid foundation in accounting principles.", 15,
             ["https://www.khanacademy.org/economics-finance-domain/core-finance"], None),
            ("Financial Management", "Understand financial statements and investment basics.", 12,
             ["https://www.khanacademy.org/economics-finance-domain/core-finance/investment-vehicles-tutorial"], None),
            ("Taxation", "Learn the fundamentals of Indian taxation.", 12,
             ["https://incometaxindia.gov.in/"], None),
            ("Business Law", "Understand the legal fundamentals relevant to commerce.", 8,
             ["https://www.khanacademy.org/economics-finance-domain"], None),
        ],
    )

    ux_roadmap = seed_roadmap(
        "ui-ux-designer-roadmap", "UI/UX Designer Roadmap",
        "From design fundamentals to a case-study-ready portfolio piece.",
        [
            ("Design Fundamentals", "Learn color, layout and typography basics.", 8,
             ["https://www.canva.com/learn/design-school/"], None),
            ("UX Foundations", "Learn user research and UX design thinking.", 12,
             ["https://www.youtube.com/c/GoogleCareerCertificates"], None),
            ("Portfolio Case Study", "Design and document a complete case study.", 15, [], None),
        ],
    )

    CAREERS = [
        dict(title="Cybersecurity Analyst", slug="cybersecurity-analyst",
             description="Protects an organization's systems and data by identifying vulnerabilities, monitoring threats, and responding to incidents.",
             required_skills=["networking", "linux", "python", "security-fundamentals", "web-security"],
             degree_backgrounds=["b-tech", "be", "bca", "mca", "b-sc"],
             portfolio_requirements="1-2 defensible security projects (e.g. a scanner or hardened login system) built and used only in your own lab environment.",
             interview_prep_notes="Expect questions on the CIA triad, common attack vectors, and how you'd respond to a basic incident scenario.",
             roadmap=cyber_roadmap),
        dict(title="Data Analyst", slug="data-analyst",
             description="Turns raw data into actionable business insight using SQL, spreadsheets, and visualization tools.",
             required_skills=["sql", "python", "data-analysis", "business-analytics"],
             degree_backgrounds=["b-tech", "bca", "mca", "b-com", "b-sc", "bba"],
             portfolio_requirements="1-2 end-to-end analysis projects with a public dataset, clean documentation, and clear business recommendations.",
             interview_prep_notes="Expect SQL query exercises, a case study, and questions about how you validate data quality.",
             roadmap=data_roadmap),
        dict(title="Software Developer", slug="software-developer",
             description="Designs, builds and maintains software applications and services.",
             required_skills=["python", "git", "data-structures", "html-css", "javascript"],
             degree_backgrounds=["b-tech", "be", "bca", "mca"],
             portfolio_requirements="A deployed full-stack project plus 2-3 smaller projects on GitHub with clear READMEs.",
             interview_prep_notes="Expect data structure/algorithm questions and a walkthrough of your strongest project.",
             roadmap=swe_roadmap),
        dict(title="Digital Marketing Manager", slug="digital-marketing-manager",
             description="Plans and runs marketing campaigns across digital channels and measures their impact.",
             required_skills=["marketing-fundamentals", "digital-marketing", "business-analytics"],
             degree_backgrounds=["bba", "mba", "b-com", "ba"],
             portfolio_requirements="A documented campaign case study with channel strategy, creative samples, and a results summary.",
             interview_prep_notes="Expect questions on channel strategy, budget allocation, and how you'd measure campaign ROI.",
             roadmap=marketing_roadmap),
        dict(title="Chartered Accountant", slug="chartered-accountant",
             description="Provides accounting, auditing, taxation and financial advisory services under India's CA qualification.",
             required_skills=["accounting-basics", "financial-management", "taxation", "business-law"],
             degree_backgrounds=["ca", "b-com", "m-com"],
             portfolio_requirements="Coursework and article-ship records as required by ICAI; this platform supports conceptual foundations alongside your formal coaching.",
             interview_prep_notes="Expect questions from your CA curriculum's core subjects — this roadmap supports foundations only.",
             roadmap=ca_roadmap),
        dict(title="UI/UX Designer", slug="ui-ux-designer",
             description="Designs digital product experiences that are usable, accessible and visually coherent.",
             required_skills=["ui-ux-design", "graphic-design"],
             degree_backgrounds=["design", "b-tech", "bca", "ba"],
             portfolio_requirements="2-3 detailed case studies showing your design process from research to final UI.",
             interview_prep_notes="Expect a portfolio walkthrough and a whiteboard design challenge.",
             roadmap=ux_roadmap),
    ]

    for c in CAREERS:
        career, created = get_or_create(Career, slug=c["slug"], defaults={
            "title": c["title"], "description": c["description"],
            "portfolio_requirements": c["portfolio_requirements"],
            "interview_prep_notes": c["interview_prep_notes"],
            "roadmap_id": c["roadmap"].id,
        })
        career.required_skills = c["required_skills"]
        career.degree_backgrounds = c["degree_backgrounds"]
        career.roadmap_id = c["roadmap"].id
        db.session.add(career)
    db.session.commit()
    print(f"Careers: {Career.query.count()}, Roadmaps: {Roadmap.query.count()}")


# ---------------------------------------------------------------------------
# Demo student + admin
# ---------------------------------------------------------------------------

def seed_admin():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@navora.app")
    admin_password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(name="NAVORA Admin", email=admin_email, role="admin", onboarding_complete=True)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin account created: {admin_email}")
    else:
        print(f"Admin account already exists: {admin_email}")


def seed_demo_student():
    demo = User.query.filter_by(email="demo.student@navora.app").first()
    if not demo:
        demo = User(name="Demo Student", email="demo.student@navora.app", role="student", onboarding_complete=True)
        demo.set_password("DemoStudent123!")
        db.session.add(demo)
        db.session.commit()

    stream = Stream.query.filter_by(slug="b-tech").first()
    profile = demo.education_profile or EducationProfile(user_id=demo.id)
    profile.stream_id = stream.id if stream else None
    profile.degree = "B.Tech"
    profile.specialization = "Information Technology"
    profile.college = "Demo Institute of Technology"
    profile.year = 2
    profile.semester = 4
    db.session.add(profile)

    dna = demo.learning_dna or LearningDNA(user_id=demo.id)
    dna.interests = ["Cybersecurity", "Software Development"]
    dna.career_goal = "Cybersecurity Analyst"
    dna.learning_style = ["video", "project-first"]
    dna.time_availability = "1_hour_per_day"
    dna.language = "English"
    dna.budget_preference = "mostly_free"
    dna.free_first_mode = True
    db.session.add(dna)
    db.session.commit()

    # Skill levels matching the spec's own Skill Gap example (section 19)
    demo_skills = {
        "python": "intermediate", "networking": "beginner", "linux": "beginner",
        "sql": "intermediate", "security-fundamentals": "beginner",
    }
    for slug, level in demo_skills.items():
        skill = Skill.query.filter_by(slug=slug).first()
        if not skill:
            continue
        us = UserSkill.query.filter_by(user_id=demo.id, skill_id=skill.id).first()
        if not us:
            us = UserSkill(user_id=demo.id, skill_id=skill.id)
        us.level = level
        db.session.add(us)
    db.session.commit()

    roadmap = Roadmap.query.filter_by(slug="cybersecurity-analyst-roadmap").first()
    if roadmap:
        progress = UserRoadmapProgress.query.filter_by(user_id=demo.id, roadmap_id=roadmap.id).first()
        if not progress:
            progress = UserRoadmapProgress(user_id=demo.id, roadmap_id=roadmap.id, current_stage_order=3)
            progress.mark_stage_complete(1)
            progress.mark_stage_complete(2)
            db.session.add(progress)
            db.session.commit()

    # Some completed / in-progress resources
    completed_urls = ["https://www.netacad.com/courses/networking", "https://linuxjourney.com/"]
    in_progress_urls = ["https://docs.python.org/3/tutorial/"]
    for url in completed_urls:
        res = Resource.query.filter_by(url=url).first()
        if res and not LearningProgress.query.filter_by(user_id=demo.id, resource_id=res.id).first():
            db.session.add(LearningProgress(
                user_id=demo.id, resource_id=res.id, status="completed", progress_pct=100,
                started_at=datetime.utcnow() - timedelta(days=20), completed_at=datetime.utcnow() - timedelta(days=10),
            ))
    for url in in_progress_urls:
        res = Resource.query.filter_by(url=url).first()
        if res and not LearningProgress.query.filter_by(user_id=demo.id, resource_id=res.id).first():
            db.session.add(LearningProgress(
                user_id=demo.id, resource_id=res.id, status="in_progress", progress_pct=45,
                started_at=datetime.utcnow() - timedelta(days=5),
            ))
    db.session.commit()

    # Study sessions -> streak
    for i in range(4):
        d = date.today() - timedelta(days=i)
        if not StudySession.query.filter_by(user_id=demo.id, date=d).first():
            db.session.add(StudySession(user_id=demo.id, date=d, minutes=45, topic="Networking"))
    db.session.commit()

    # A bookmark and a planned project
    scanner = _project_by_title("Network Port Scanner")
    if scanner and not UserProject.query.filter_by(user_id=demo.id, project_id=scanner.id).first():
        db.session.add(UserProject(user_id=demo.id, project_id=scanner.id, status="planned"))

    owasp = Resource.query.filter_by(url="https://owasp.org/www-project-top-ten/").first()
    if owasp and not Bookmark.query.filter_by(user_id=demo.id, target_type="resource", target_id=owasp.id).first():
        db.session.add(Bookmark(user_id=demo.id, target_type="resource", target_id=owasp.id, folder="Career"))
    db.session.commit()

    print(f"Demo student ready: {demo.email} / DemoStudent123!")


def main():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        db.create_all()
        seed_streams()
        seed_skills()
        seed_resources()
        seed_projects()
        seed_careers_and_roadmaps()
        seed_admin()
        seed_demo_student()
        print("\nSeed complete.")


if __name__ == "__main__":
    main()
