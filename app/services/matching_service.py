import re


# --------------------------------------------------
# 1. STUDENT SKILL GROUPS
# --------------------------------------------------

STUDENT_SKILL_MAP = {
    "python & backend": ["python"],
    "databases & sql": ["sql", "mysql", "postgresql"],
    "javascript/typescript": ["javascript", "typescript"],
    "react/next.js": ["react", "next.js"],
    "llm api integration": ["llm", "api"],
}


# --------------------------------------------------
# 2. JOB ROLE SKILL EXPANSION
# --------------------------------------------------

JOB_SKILL_MAP = {
    "website development": ["html", "css", "javascript"],
    "web development": ["html", "css", "javascript"],
    "frontend development": ["html", "css", "javascript", "react"],
    "backend development": ["python", "sql", "flask", "django", "node.js"],
}


# --------------------------------------------------
# 3. SKILL ALIASES
# --------------------------------------------------

SKILL_ALIASES = {
    "llms": "llm",
    "rest apis": "api",
    "rest api": "api",
    "scikit learn": "scikit-learn",
    "nextjs": "next.js",
    "nodejs": "node.js",
    "communication skills": "communication",
    "artificial intelligence (ai)": "artificial intelligence",
    "customer relationship management": "crm",
    "client relationship management": "crm",
}


# --------------------------------------------------
# 4. RELATED SKILL MAPPING
# --------------------------------------------------

RELATED_SKILL_MAP = {
    "market research": [
        "shopper research",
        "consumer research",
        "market analysis",
    ],

    "sales": [
        "b2b sales",
        "field sales",
        "sales management",
        "real estate sales",
        "travel sales",
    ],

    "lead generation": [
        "cold calling",
        "prospecting",
        "lead management",
    ],

    "business development": [
        "partnerships",
        "client acquisition",
        "b2b sales",
    ],

    "digital marketing": [
        "seo",
        "content marketing",
        "social media marketing",
        "email marketing",
        "campaign management",
    ],

    "crm": [
        "customer relationship management",
        "client relationship management",
    ],
}


# --------------------------------------------------
# 5. SKILLS RECOGNIZED FROM RESUMES
# --------------------------------------------------

SKILL_LIST = [
    "python",
    "java",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "next.js",
    "sql",
    "mysql",
    "postgresql",
    "flask",
    "django",
    "node.js",
    "excel",
    "machine learning",
    "artificial intelligence",
    "data analysis",
    "git",
    "docker",
    "api",
    "llm",
    "pandas",
    "scikit-learn",
    "communication",
    "digital marketing",
    "email marketing",
    "market research",
    "shopper research",
    "consumer research",
    "market analysis",
    "b2b sales",
    "cold calling",
    "prospecting",
    "lead management",
    "seo",
    "social media marketing",
    "business development",
    "lead generation",
    "ms office",
    "crm",
    "negotiation",
    "sales",
    "sales management",
    "real estate sales",
    "linkedin",
    "canva",
    "google sheets",
    "travel sales",
    "itinerary planning",
    "recruitment",
    "candidate screening",
    "onboarding",
    "partnerships",
    "networking",
    "presentations",
    "field sales",
    "aws",
    "content marketing",
    "campaign management",
    "google analytics",
    "brand management",
    "trade marketing",
    "client acquisition",
    "inventory management",
    "supply chain management",
    "stakeholder management",
    "product management",
    "customer experience",
    "meta ads",
    "sem",
    "influencer marketing",
    "retail strategy",
    "gtm strategy",
    "email campaigns",
    "c++",
    "express.js",
    "mongodb",
    "github",
]


# --------------------------------------------------
# 6. NORMALIZE SKILLS
# --------------------------------------------------

def normalize_skill(skill):

    if not isinstance(skill, str):
        return ""

    skill = skill.lower().strip()
    skill = re.sub(r"\s+", " ", skill)

    return SKILL_ALIASES.get(skill, skill)


# --------------------------------------------------
# 7. EXPAND STUDENT SKILL GROUPS
# --------------------------------------------------


def expand_student_skill(skill):

    skill = normalize_skill(skill).strip()

    if not skill:
        return []

    if skill in STUDENT_SKILL_MAP:
        return STUDENT_SKILL_MAP[skill]

    # Remove category names
    if ":" in skill:
        skill = skill.split(":", 1)[1]

    expanded_skills = []

    # Split multiple skills
    for item in skill.split(","):

        item = normalize_skill(item).strip()

        if item in SKILL_ALIASES:
            item = SKILL_ALIASES[item]

        # Keep only recognized skills
        if item in SKILL_LIST:
            expanded_skills.append(item)

    return expanded_skills


# --------------------------------------------------
# 8. EXTRACT SKILLS FROM RESUME TEXT
# --------------------------------------------------

def extract_skills_from_resume(resume_text):

    if not isinstance(resume_text, str):
        return set()

    resume_text = resume_text.lower()
    found_skills = set()

    for skill in SKILL_LIST:

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(skill)
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, resume_text):
            found_skills.add(normalize_skill(skill))

    # Alternative skill names
    for alias, standard_skill in SKILL_ALIASES.items():

        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(alias)
            + r"(?![a-z0-9])"
        )

        if re.search(pattern, resume_text):
            found_skills.add(standard_skill)

    return found_skills


# --------------------------------------------------
# 9. GET ALL STUDENT SKILLS
# --------------------------------------------------

def get_student_skills(student):

    skills = set()

    if isinstance(student, dict):

        # Profile skills
        for field in ["all_skills", "skills", "resume_skills"]:

            field_skills = student.get(field) or []

            if isinstance(field_skills, str):
                field_skills = [field_skills]

            for skill in field_skills:
                skills.update(expand_student_skill(skill))

        # Resume content
        resume = student.get("resume") or {}

        if isinstance(resume, dict):

            for field in ["text", "summary"]:

                skills.update(
                    extract_skills_from_resume(
                        resume.get(field, "")
                    )
                )

        elif isinstance(resume, str):

            skills.update(
                extract_skills_from_resume(resume)
            )

        # Experience details
        experiences = student.get("experience") or []

        if isinstance(experiences, dict):
            experiences = [experiences]

        for experience in experiences:

            if not isinstance(experience, dict):
                continue

            experience_skills = experience.get("skills") or []

            if isinstance(experience_skills, str):
                experience_skills = [experience_skills]

            for skill in experience_skills:
                skills.update(expand_student_skill(skill))

            skills.update(
                extract_skills_from_resume(
                    experience.get("description", "")
                )
            )

            skills.update(
                extract_skills_from_resume(
                    experience.get("title", "")
                )
            )

        # Headline and bio
        for field in ["headline", "bio"]:

            skills.update(
                extract_skills_from_resume(
                    student.get(field, "")
                )
            )

    elif isinstance(student, (list, set, tuple)):

        for skill in student:
            skills.update(expand_student_skill(skill))

    return skills


# --------------------------------------------------
# 10. GET JOB REQUIRED SKILLS
# --------------------------------------------------

def get_job_skills(job):

    if isinstance(job, dict):
        job_skills = job.get("required_skills") or []

        job_text = " ".join([
            str(job.get("title") or ""),
            str(job.get("role_title") or ""),
            str(job.get("category") or ""),
            str(job.get("description") or ""),
            str(job.get("brief") or ""),
            str(job.get("deliverables") or "")
        ])

    else:
        job_skills = job
        job_text = ""

    if isinstance(job_skills, str):
        job_skills = [job_skills]

    skills = set()

    # Extract skills from job requirements
    for skill in job_skills:

        skill = normalize_skill(skill)

        if not skill:
            continue

        if skill in JOB_SKILL_MAP:
            skills.update(JOB_SKILL_MAP[skill])
        else:
            skills.add(skill)

    # Extract skills from job description
    skills.update(extract_skills_from_resume(job_text))

    return skills


# --------------------------------------------------
# 11. CHECK EXACT AND RELATED SKILL MATCHES
# --------------------------------------------------

def find_skill_matches(required_skills, student_skills):

    matched_skills = set()
    missing_skills = set()
    related_matches = {}

    used_student_skills = set()

    # First priority: Exact matches
    for required_skill in sorted(required_skills):

        if required_skill in student_skills:
            matched_skills.add(required_skill)
            used_student_skills.add(required_skill)

    # Second priority: Related matches
    for required_skill in sorted(required_skills):

        if required_skill in matched_skills:
            continue

        related_skills = RELATED_SKILL_MAP.get(
            required_skill, []
        )

        for skill in related_skills:

            if skill in student_skills and skill not in used_student_skills:

                matched_skills.add(required_skill)
                used_student_skills.add(skill)

                related_matches[required_skill] = [skill]
                break

        if required_skill not in matched_skills:
            missing_skills.add(required_skill)

    return matched_skills, missing_skills, related_matches

# --------------------------------------------------
# 12. CALCULATE MATCHING PERCENTAGE
# --------------------------------------------------

def match_resume_with_job(job_skills, student):

    student_skills = get_student_skills(student)
    required_skills = get_job_skills(job_skills)

    if not required_skills:

        return {
            "match_percentage": 0,
            "matched_skills": [],
            "missing_skills": [],
            "related_matches": {},
        }

    matched_skills, missing_skills, related_matches = (
        find_skill_matches(
            required_skills,
            student_skills
        )
    )

    percentage = (
        len(matched_skills) / len(required_skills)
    ) * 100

    return {
        "match_percentage": round(percentage, 2),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "related_matches": related_matches,
    }


# --------------------------------------------------
# 13. SHORTLIST STUDENTS
# --------------------------------------------------

def shortlist_student(job_skills, student, threshold=60):

    result = match_resume_with_job(
        job_skills,
        student
    )

    result["eligible"] = (
        result["match_percentage"] >= threshold
    )

    return result


# --------------------------------------------------
# 14. RANK STUDENTS
# --------------------------------------------------

def rank_students(job_skills, students, threshold=60):

    results = []

    for student in students:

        result = shortlist_student(
            job_skills,
            student,
            threshold
        )

        results.append({
            "student_id": student.get(
                "id",
                student.get("student_id")
            ),
            **result
        })

    # Highest matching percentage first
    results.sort(
        key=lambda student: student["match_percentage"],
        reverse=True
    )

    return results
