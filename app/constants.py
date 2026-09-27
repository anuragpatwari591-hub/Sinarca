"""Static choice-lists used across onboarding forms, admin forms, and seeding.

Kept in one place instead of scattered magic strings through routes/templates.
"""

INTEREST_AREAS = [
    "Software Development", "Artificial Intelligence", "Cybersecurity", "Finance",
    "Marketing", "Management", "Design", "Data Analytics", "Entrepreneurship",
    "Consulting", "Research", "Government Exams", "Accounting", "Law",
]

CAREER_GOAL_SUGGESTIONS = [
    "Software Developer", "Data Analyst", "Cybersecurity Analyst", "Product Manager",
    "Investment Banking Analyst", "Chartered Accountant", "Marketing Manager",
    "Management Consultant", "Entrepreneur", "Researcher", "UI/UX Designer",
]

LEARNING_STYLES = [
    ("video", "Video lessons"),
    ("reading", "Reading / articles"),
    ("interactive", "Interactive / hands-on"),
    ("practice-first", "Practice-first"),
    ("project-first", "Project-first"),
    ("short-tutorials", "Short tutorials"),
    ("long-form", "Long-form lectures"),
    ("visual", "Visual explanations"),
]

TIME_AVAILABILITY = [
    ("30_min_per_day", "30 minutes / day"),
    ("1_hour_per_day", "1 hour / day"),
    ("2_hours_per_day", "2 hours / day"),
    ("3_plus_hours_per_day", "3+ hours / day"),
]

LANGUAGES = ["English", "Hindi", "Bengali"]

BUDGET_PREFERENCES = [
    ("completely_free", "Completely free"),
    ("mostly_free", "Mostly free"),
    ("open_to_paid", "Open to paid courses"),
    ("premium_ok", "Premium learning acceptable"),
]

DEGREES = [
    "B.Tech", "B.E.", "BCA", "MCA", "BBA", "MBA", "B.Com", "M.Com", "CA", "CS",
    "CMA", "BA", "MA", "B.Sc", "M.Sc", "Law", "Design", "Pharmacy", "Other",
]

STUDENT_YEARS = [1, 2, 3, 4, 5]

DIFFICULTIES = ["beginner", "intermediate", "advanced"]

RESOURCE_TYPES = ["video", "article", "docs", "course", "book", "practice", "project"]

REPORT_TYPES = [
    ("broken_link", "Broken link"),
    ("outdated", "Outdated content"),
    ("misleading", "Misleading information"),
    ("wrong_category", "Incorrect category"),
    ("wrong_price", "Wrong price"),
]

FEEDBACK_REASONS = [
    ("too_difficult", "Too difficult"),
    ("too_long", "Too long"),
    ("boring", "Boring"),
    ("wrong_topic", "Wrong topic"),
    ("already_knew", "Already knew this"),
    ("wrong_style", "Wrong learning style"),
    ("not_relevant", "Not relevant"),
]

BOOKMARK_FOLDERS = ["Learn Later", "Projects", "Interview", "Semester", "Career"]

CHATBOT_MODES = [
    ("explain", "Explain"),
    ("quiz", "Quiz Me"),
    ("plan_day", "Plan My Day"),
    ("find_resources", "Find Resources"),
    ("project_ideas", "Project Ideas"),
    ("revision", "Revision"),
    ("career_guidance", "Career Guidance"),
]
