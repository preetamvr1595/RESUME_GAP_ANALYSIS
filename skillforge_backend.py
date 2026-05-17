from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import re
import math
import uuid
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import PyPDF2
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import datetime

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
REPORTS_FOLDER = os.path.join(os.getcwd(), 'reports')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# ─────────────────────────────────────────────
# SKILL DATABASE
# ─────────────────────────────────────────────
SKILL_DATABASE = {
    "programming": ["python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "kotlin", "swift", "scala", "r", "matlab", "php", "perl", "cobol", "fortran", "julia", "dart", "solidity"],
    "web": ["html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "fastapi", "spring", "laravel", "next.js", "nuxt", "tailwind", "bootstrap", "jquery", "rest api", "graphql", "webpack", "vite", "sass", "less", "redux", "rxjs", "pwa", "spa"],
    "data_science": ["machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "plotly", "data analysis", "statistical analysis", "feature engineering", "model deployment", "reinforcement learning", "pyspark", "xgboost", "nltk", "spacy", "genai", "llm", "bert", "gpt"],
    "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "cassandra", "elasticsearch", "firebase", "dynamodb", "neo4j", "mariadb", "db2", "cosmos db"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins", "ci/cd", "devops", "linux", "bash", "shell scripting", "serverless", "lambda", "cloudfront", "s3", "ec2", "iam", "eks", "gke", "aks"],
    "data_tools": ["tableau", "power bi", "excel", "spark", "hadoop", "kafka", "airflow", "dbt", "snowflake", "bigquery", "presto", "superset", "metabase", "looker"],
    "soft_skills": ["communication", "teamwork", "leadership", "problem solving", "critical thinking", "project management", "agile", "scrum", "kanban", "time management", "conflict resolution"],
    "security": ["cybersecurity", "network security", "penetration testing", "ethical hacking", "cryptography", "owasp", "siem", "firewall", "idm", "soc", "vulnerability assessment"],
    "mobile": ["android", "ios", "react native", "flutter", "xamarin", "objective-c", "swiftui", "java", "kotlin"],
}

ALL_SKILLS = []
for cat, skills in SKILL_DATABASE.items():
    for skill in skills:
        ALL_SKILLS.append({"skill": skill, "category": cat})

SKILL_LEARNING_DATA = {
    "python": {
        "difficulty": "Beginner",
        "priority": "High",
        "time": "4 weeks",
        "why": "Most in-demand language for AI/ML, data science, and backend development.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "course": "https://www.coursera.org/learn/python",
            "kaggle": "https://www.kaggle.com/learn/python",
            "project": "Build a data pipeline or REST API"
        }
    },
    "machine learning": {
        "difficulty": "Intermediate",
        "priority": "High",
        "time": "8 weeks",
        "why": "Core skill for AI/data science roles, enables predictive modelling.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=gmvvaobm7eQ",
            "course": "https://www.coursera.org/learn/machine-learning",
            "kaggle": "https://www.kaggle.com/learn/intro-to-machine-learning",
            "project": "Train a classifier on Titanic dataset"
        }
    },
    "sql": {
        "difficulty": "Beginner",
        "priority": "High",
        "time": "3 weeks",
        "why": "Universal skill for data querying used in nearly every tech role.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "course": "https://www.coursera.org/learn/sql-for-data-science",
            "kaggle": "https://www.kaggle.com/learn/intro-to-sql",
            "project": "Build a sales analytics dashboard with SQL"
        }
    },
    "deep learning": {
        "difficulty": "Advanced",
        "priority": "High",
        "time": "10 weeks",
        "why": "Powers modern AI applications including NLP and computer vision.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=aircAruvnKk",
            "course": "https://www.coursera.org/specializations/deep-learning",
            "kaggle": "https://www.kaggle.com/learn/intro-to-deep-learning",
            "project": "Build an image classifier with CNN"
        }
    },
    "docker": {
        "difficulty": "Intermediate",
        "priority": "Medium",
        "time": "2 weeks",
        "why": "Essential for containerizing apps and modern DevOps workflows.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=3c-iBn73dDE",
            "course": "https://www.udemy.com/course/docker-mastery/",
            "kaggle": None,
            "project": "Containerize a Flask app with Docker"
        }
    },
    "aws": {
        "difficulty": "Intermediate",
        "priority": "High",
        "time": "6 weeks",
        "why": "Market-leading cloud platform with massive job demand.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=ulprqHHWlng",
            "course": "https://aws.amazon.com/training/",
            "kaggle": None,
            "project": "Deploy a web app on EC2 with S3 storage"
        }
    },
    "react": {
        "difficulty": "Intermediate",
        "priority": "High",
        "time": "5 weeks",
        "why": "Most popular frontend framework, used at Facebook, Airbnb, Netflix.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=w7ejDZ8SWv8",
            "course": "https://www.coursera.org/learn/react-basics",
            "kaggle": None,
            "project": "Build a full-stack todo app with React + Node"
        }
    },
    "tensorflow": {
        "difficulty": "Advanced",
        "priority": "High",
        "time": "6 weeks",
        "why": "Industry-standard ML framework for production AI systems.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=tPYj3fFJGjk",
            "course": "https://www.coursera.org/learn/introduction-tensorflow",
            "kaggle": "https://www.kaggle.com/learn/intro-to-deep-learning",
            "project": "Build a sentiment analysis model"
        }
    },
    "nlp": {
        "difficulty": "Advanced",
        "priority": "High",
        "time": "8 weeks",
        "why": "Powers chatbots, search engines, and intelligent document processing.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=8S3qHHUKqYk",
            "course": "https://www.coursera.org/specializations/natural-language-processing",
            "kaggle": "https://www.kaggle.com/learn/natural-language-processing",
            "project": "Build a text classifier or chatbot"
        }
    },
    "kubernetes": {
        "difficulty": "Advanced",
        "priority": "Medium",
        "time": "6 weeks",
        "why": "Standard for orchestrating containers at scale in production.",
        "resources": {
            "youtube": "https://www.youtube.com/watch?v=X48VuDVv0do",
            "course": "https://www.udemy.com/course/learn-kubernetes/",
            "kaggle": None,
            "project": "Deploy a microservices app on Kubernetes"
        }
    },
}

# Default resource for unknown skills
def get_default_resource(skill):
    return {
        "difficulty": "Intermediate",
        "priority": "Medium",
        "time": "4 weeks",
        "why": f"{skill.title()} is a sought-after skill that can significantly boost your career profile.",
        "resources": {
            "youtube": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial",
            "course": f"https://www.coursera.org/search?query={skill.replace(' ', '+')}",
            "kaggle": f"https://www.kaggle.com/search?q={skill.replace(' ', '+')}",
            "project": f"Build a project demonstrating {skill} skills"
        }
    }

# ─────────────────────────────────────────────
# TEXT PROCESSING
# ─────────────────────────────────────────────
def extract_text_from_pdf(file_obj):
    try:
        reader = PyPDF2.PdfReader(file_obj)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return ""

def clean_text(text):
    text = text.lower()
    # Keep alphanumeric, spaces, and specific tech symbols
    text = re.sub(r'[^\w\s\.\+#\-/]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skills(text):
    if not text:
        return []
    text_lower = " " + text.lower() + " "
    # Replace common punctuation with spaces to allow boundaries, but preserve tech-specific ones
    text_lower = re.sub(r'[,;:\(\)\[\]\{\}]', ' ', text_lower)
    
    found = []
    for item in ALL_SKILLS:
        skill = item["skill"].lower()
        
        # More robust matching that handles C++, C#, .NET, Node.js, etc.
        # We look for the skill surrounded by non-alphanumeric (or start/end)
        # But we must be careful with skill having internal special chars
        
        # Escape for regex
        escaped_skill = re.escape(skill)
        
        # Boundary logic: 
        # Left boundary: start of string or non-char (excluding symbols in tech names like .+#-)
        # Right boundary: end of string or non-char
        pattern = r'(?<=[\s\d\W])' + escaped_skill + r'(?=[\s\d\W])'
        
        if re.search(pattern, text_lower):
            found.append(item)
            
    # Deduplicate by name
    unique_found = []
    seen = set()
    for f in found:
        if f["skill"] not in seen:
            unique_found.append(f)
            seen.add(f["skill"])
            
    return unique_found

def extract_experience_level(text):
    text_lower = text.lower()
    years_match = re.findall(r'(\d+)\s*\+?\s*years?\s*(?:of\s*)?(?:experience|exp)', text_lower)
    if years_match:
        max_years = max(int(y) for y in years_match)
        if max_years >= 7:
            return "Senior", max_years
        elif max_years >= 3:
            return "Intermediate", max_years
        else:
            return "Beginner", max_years
    if any(w in text_lower for w in ["senior", "lead", "principal", "architect"]):
        return "Senior", 6
    if any(w in text_lower for w in ["junior", "fresher", "graduate", "intern", "entry"]):
        return "Beginner", 0
    return "Intermediate", 2

def predict_job_role(skills_list):
    skill_names = [s["skill"] for s in skills_list]
    skill_set = set(skill_names)
    
    role_scores = {
        "Data Scientist": len(skill_set & {"python", "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "nlp", "statistics"}),
        "Full Stack Developer": len(skill_set & {"react", "node.js", "javascript", "html", "css", "sql", "mongodb", "express", "rest api"}),
        "Backend Developer": len(skill_set & {"python", "java", "sql", "postgresql", "mongodb", "docker", "aws", "redis", "flask", "django", "spring"}),
        "DevOps Engineer": len(skill_set & {"docker", "kubernetes", "aws", "azure", "jenkins", "ci/cd", "terraform", "ansible", "linux", "bash"}),
        "ML Engineer": len(skill_set & {"machine learning", "python", "tensorflow", "pytorch", "docker", "aws", "mlops", "deep learning", "sql"}),
        "Frontend Developer": len(skill_set & {"react", "angular", "vue", "html", "css", "javascript", "typescript", "next.js", "tailwind"}),
        "Data Engineer": len(skill_set & {"sql", "python", "spark", "kafka", "airflow", "aws", "bigquery", "snowflake", "postgresql"}),
        "Cybersecurity Analyst": len(skill_set & {"cybersecurity", "network security", "penetration testing", "linux", "python", "cryptography"}),
    }
    
    if not any(role_scores.values()):
        return "Software Developer"
    return max(role_scores, key=role_scores.get)

def calculate_resume_score(resume_text, resume_skills, experience_level):
    score = 0
    # Skills diversity
    score += min(len(resume_skills) * 3, 30)
    # Experience
    exp_scores = {"Beginner": 10, "Intermediate": 20, "Senior": 30}
    score += exp_scores.get(experience_level, 10)
    # Length / detail
    word_count = len(resume_text.split())
    score += min(word_count // 50, 20)
    # Has email/contact
    if re.search(r'[\w.-]+@[\w.-]+', resume_text):
        score += 5
    # Has metrics/numbers
    numbers = re.findall(r'\d+%|\d+\+', resume_text)
    score += min(len(numbers) * 2, 15)
    return min(score, 100)

# ─────────────────────────────────────────────
# CORE ANALYSIS ENGINE
# ─────────────────────────────────────────────
def analyze_resume_jd(resume_text, jd_text):
    clean_resume = clean_text(resume_text)
    clean_jd = clean_text(jd_text)

    # TF-IDF Cosine Similarity
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        cosine_sim = 0.5

    match_pct = round(cosine_sim * 100, 1)
    match_pct = max(15.0, min(match_pct, 95.0))  # realistic range

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    resume_skill_names = set(s["skill"] for s in resume_skills)
    jd_skill_names = set(s["skill"] for s in jd_skills)

    matched = resume_skill_names & jd_skill_names
    missing = jd_skill_names - resume_skill_names
    extra = resume_skill_names - jd_skill_names

    # Boost match score based on skill overlap
    if jd_skill_names:
        skill_overlap = len(matched) / len(jd_skill_names)
        match_pct = round((match_pct * 0.5 + skill_overlap * 100 * 0.5), 1)

    experience_level, years = extract_experience_level(resume_text)
    predicted_role = predict_job_role(resume_skills)
    resume_score = calculate_resume_score(resume_text, resume_skills, experience_level)

    # Skill confidence scores
    skill_confidence = {}
    for skill in resume_skill_names:
        count = len(re.findall(r'\b' + re.escape(skill) + r'\b', resume_text.lower()))
        skill_confidence[skill] = min(count * 20, 100)

    # Domain strengths
    domain_strength = {}
    for cat, skills in SKILL_DATABASE.items():
        found = len(resume_skill_names & set(skills))
        total = len(skills)
        domain_strength[cat] = round((found / total) * 100, 1) if total > 0 else 0

    # AI Insights
    insights = generate_insights(
        match_pct, resume_skills, missing, extra,
        experience_level, predicted_role, resume_score, resume_text
    )

    # Missing skill details
    missing_skill_details = []
    for skill in list(missing)[:12]:
        data = SKILL_LEARNING_DATA.get(skill, get_default_resource(skill))
        missing_skill_details.append({
            "skill": skill,
            "difficulty": data["difficulty"],
            "priority": data["priority"],
            "time": data["time"],
            "why": data["why"],
            "resources": data["resources"]
        })

    # Roadmap generation
    roadmap = generate_roadmap(experience_level, predicted_role, missing_skill_details)

    return {
        "match_percentage": match_pct,
        "resume_score": resume_score,
        "predicted_role": predicted_role,
        "experience_level": experience_level,
        "years_experience": years,
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "extra_skills": sorted(list(extra)),
        "resume_skills": sorted(list(resume_skill_names)),
        "jd_skills": sorted(list(jd_skill_names)),
        "domain_strength": domain_strength,
        "skill_confidence": skill_confidence,
        "missing_skill_details": missing_skill_details,
        "roadmap": roadmap,
        "insights": insights,
    }

def generate_insights(match_pct, resume_skills, missing, extra, exp_level, role, score, resume_text):
    strengths = []
    weaknesses = []
    suggestions = []

    if match_pct >= 70:
        strengths.append("Strong overall alignment with job requirements.")
    elif match_pct >= 50:
        strengths.append("Moderate skill overlap with the job description.")
    else:
        weaknesses.append("Low alignment with job requirements — significant upskilling needed.")

    if len(resume_skills) >= 10:
        strengths.append(f"Diverse technical portfolio with {len(resume_skills)} identified skills.")
    elif len(resume_skills) >= 5:
        strengths.append(f"Solid skill base with {len(resume_skills)} technical competencies.")
    else:
        weaknesses.append("Limited skill keywords detected — expand your technical vocabulary.")

    if len(missing) > 5:
        weaknesses.append(f"{len(missing)} required skills are missing from your resume.")
        suggestions.append("Prioritize learning the top 3 missing skills within 60 days.")
    
    if exp_level == "Senior":
        strengths.append("Senior-level experience detected — strong candidate profile.")
    elif exp_level == "Beginner":
        weaknesses.append("Limited experience detected — consider internship or project-based experience.")
        suggestions.append("Build 2-3 portfolio projects showcasing required skills.")

    if score >= 75:
        strengths.append("High resume quality score — well-structured document.")
    elif score < 50:
        weaknesses.append("Resume quality needs improvement — add metrics and quantifiable achievements.")
        suggestions.append("Use numbers: 'Improved performance by 30%' instead of 'Improved performance'.")

    word_count = len(resume_text.split())
    if word_count < 200:
        suggestions.append("Resume appears too brief — expand with detailed project descriptions.")
        weaknesses.append("Resume length is below recommended (300+ words).")

    if not re.search(r'github|gitlab|portfolio|linkedin', resume_text.lower()):
        suggestions.append("Add GitHub profile or portfolio link to stand out.")

    suggestions.append(f"Tailor your resume with keywords specific to the {role} role.")
    suggestions.append("Add a professional summary section targeting this job role.")

    time_to_job = "3-4 months" if match_pct >= 70 else "5-8 months" if match_pct >= 50 else "9-12 months"

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "time_to_job": time_to_job,
        "overall_feedback": f"Your resume shows a {match_pct}% match for this role. {'You are a strong candidate with minor gaps to fill.' if match_pct >= 70 else 'With targeted upskilling, you can become competitive for this role.' if match_pct >= 50 else 'Significant preparation is needed, but a structured plan will get you there.'}"
    }

def generate_roadmap(exp_level, role, missing_skills):
    phases = []
    
    high_priority = [s for s in missing_skills if s["priority"] == "High"][:3]
    med_priority = [s for s in missing_skills if s["priority"] == "Medium"][:2]

    month = 1
    if high_priority:
        phases.append({
            "phase": f"Month {month}-{month+1}",
            "title": "Foundation Building",
            "description": f"Master the high-priority skills required for {role}",
            "tasks": [f"Learn {s['skill'].title()} ({s['time']})" for s in high_priority],
            "milestone": "Complete core skill certifications"
        })
        month += 2

    phases.append({
        "phase": f"Month {month}",
        "title": "Hands-On Practice",
        "description": "Apply learned skills through real projects",
        "tasks": ["Build 2 portfolio projects", "Contribute to open source", "Document everything on GitHub"],
        "milestone": "Launch 2 live portfolio projects"
    })
    month += 1

    if med_priority:
        phases.append({
            "phase": f"Month {month}",
            "title": "Skill Expansion",
            "description": "Add supporting skills to broaden your profile",
            "tasks": [f"Learn {s['skill'].title()}" for s in med_priority] + ["Take mock interviews"],
            "milestone": "Achieve mid-level proficiency in all key areas"
        })
        month += 1

    phases.append({
        "phase": f"Month {month}",
        "title": "Job Preparation",
        "description": "Optimize resume, prepare for interviews",
        "tasks": ["Update resume with new skills", "Practice LeetCode/system design", "Apply to 10+ positions/week"],
        "milestone": "Land first interview or job offer"
    })

    return phases

# ─────────────────────────────────────────────
# REPORT GENERATION
# ─────────────────────────────────────────────
def generate_pdf_report(data, resume_text, jd_text, user_name="Candidate"):
    report_id = str(uuid.uuid4())[:8]
    report_path = f"{REPORTS_FOLDER}/SkillForge_Report_{report_id}.pdf"
    
    doc = SimpleDocTemplate(report_path, pagesize=A4,
                             rightMargin=40, leftMargin=40,
                             topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    story = []

    # Header
    header_style = ParagraphStyle('Header', fontSize=22, textColor=colors.HexColor('#6C63FF'),
                                   fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
    sub_style = ParagraphStyle('Sub', fontSize=11, textColor=colors.HexColor('#888888'),
                                alignment=TA_CENTER, spaceAfter=20)
    
    story.append(Paragraph("SkillForge AI", header_style))
    story.append(Paragraph("Intelligent Resume Analyzer &amp; Career Report", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#6C63FF')))
    story.append(Spacer(1, 12))

    # Candidate Info
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    info_data = [
        ['Candidate:', user_name, 'Date:', date_str],
        ['Predicted Role:', data['predicted_role'], 'Experience:', data['experience_level']],
    ]
    info_table = Table(info_data, colWidths=[100, 180, 80, 150])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#6C63FF')),
        ('TEXTCOLOR', (2,0), (2,-1), colors.HexColor('#6C63FF')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # Score Cards
    score_title = ParagraphStyle('STitle', fontSize=14, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#1a1a2e'), spaceAfter=8)
    story.append(Paragraph("📊 Performance Overview", score_title))
    
    score_data = [
        ['Match %', 'Resume Score', 'Missing Skills', 'Time to Job'],
        [f"{data['match_percentage']}%", f"{data['resume_score']}/100",
         str(len(data['missing_skills'])), data['insights']['time_to_job']]
    ]
    score_table = Table(score_data, colWidths=[118, 118, 118, 118])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#6C63FF')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f0eeff')),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,1), 16),
        ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#6C63FF')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.HexColor('#6C63FF'), colors.HexColor('#f0eeff')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 16))

    # AI Feedback
    story.append(Paragraph("🤖 AI Insights", score_title))
    feedback_style = ParagraphStyle('Feedback', fontSize=10, textColor=colors.HexColor('#333333'),
                                     leading=16, spaceAfter=6)
    story.append(Paragraph(data['insights']['overall_feedback'], feedback_style))
    story.append(Spacer(1, 8))

    # Strengths & Weaknesses
    sw_data = [['✅ Strengths', '⚠️ Areas to Improve']]
    max_len = max(len(data['insights']['strengths']), len(data['insights']['weaknesses']), 1)
    for i in range(max_len):
        s = f"• {data['insights']['strengths'][i]}" if i < len(data['insights']['strengths']) else ""
        w = f"• {data['insights']['weaknesses'][i]}" if i < len(data['insights']['weaknesses']) else ""
        sw_data.append([s, w])
    
    sw_table = Table(sw_data, colWidths=[237, 237])
    sw_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#00b894')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#e17055')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#eeeeee')),
    ]))
    story.append(sw_table)
    story.append(Spacer(1, 16))

    # Skills
    story.append(Paragraph("🎯 Skills Analysis", score_title))
    
    matched_str = ", ".join(data['matched_skills'][:20]) or "None identified"
    missing_str = ", ".join(data['missing_skills'][:20]) or "None — Great match!"
    
    skills_data = [
        ['Category', 'Skills'],
        ['✅ Matched Skills', matched_str],
        ['❌ Missing Skills', missing_str],
    ]
    skills_table = Table(skills_data, colWidths=[130, 344])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d2d2d')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#e8f8f5')),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#ffeaea')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 16))

    # Career Roadmap
    story.append(Paragraph("🗺️ Career Roadmap", score_title))
    for phase in data['roadmap']:
        phase_style = ParagraphStyle('Phase', fontSize=10, fontName='Helvetica-Bold',
                                      textColor=colors.HexColor('#6C63FF'), spaceAfter=4)
        story.append(Paragraph(f"📍 {phase['phase']} — {phase['title']}", phase_style))
        for task in phase['tasks']:
            task_style = ParagraphStyle('Task', fontSize=9, leftIndent=16, spaceAfter=2)
            story.append(Paragraph(f"  → {task}", task_style))
        milestone_style = ParagraphStyle('MS', fontSize=9, leftIndent=16,
                                          textColor=colors.HexColor('#00b894'), spaceAfter=8)
        story.append(Paragraph(f"  🏆 Milestone: {phase['milestone']}", milestone_style))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#eeeeee')))
    footer_style = ParagraphStyle('Footer', fontSize=8, textColor=colors.HexColor('#999999'),
                                   alignment=TA_CENTER, spaceBefore=6)
    story.append(Paragraph("Generated by SkillForge AI | Career Intelligence Platform", footer_style))

    doc.build(story)
    return report_path

def generate_standard_resume_pdf(data, user_name="Candidate"):
    report_id = str(uuid.uuid4())[:8]
    resume_path = f"{REPORTS_FOLDER}/Standard_Resume_{report_id}.pdf"
    
    doc = SimpleDocTemplate(resume_path, pagesize=A4,
                             rightMargin=50, leftMargin=50,
                             topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    story = []

    # Name Header
    name_style = ParagraphStyle('Name', fontSize=24, textColor=colors.black,
                                 fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=2)
    story.append(Paragraph(user_name.upper(), name_style))
    
    sub_style = ParagraphStyle('Sub', fontSize=12, textColor=colors.HexColor('#666666'),
                                alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph(data['predicted_role'], sub_style))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 12))

    # Summary
    section_style = ParagraphStyle('Section', fontSize=14, fontName='Helvetica-Bold',
                                    textColor=colors.black, spaceAfter=10)
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
    
    summary_text = f"Accomplished {data['predicted_role']} professional with {data['years_experience']}+ years of industry experience. " \
                   f"Expertise in {', '.join(data['matched_skills'][:5])}. Strong background in {data['experience_level']} " \
                   f"level implementations, system optimization, and data-driven problem solving."
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 15))

    # Skills
    story.append(Paragraph("TECHNICAL COMPETENCIES", section_style))
    all_skills = data['matched_skills'] + data['extra_skills']
    skills_data = [
        ['Core Expertise', ", ".join(all_skills[:10])],
        ['Tools & Platforms', ", ".join(all_skills[10:20] if len(all_skills) > 10 else ["General Purpose Libraries"])]
    ]
    skills_table = Table(skills_data, colWidths=[120, 360])
    skills_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 15))

    # Experience Placeholder
    story.append(Paragraph("WORK EXPERIENCE", section_style))
    story.append(Paragraph(f"<b>Senior {data['predicted_role']} Specialist</b>", styles['Normal']))
    story.append(Paragraph(f"Global Technology Solutions | 2020 – Present", styles['Normal']))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"• Spearheaded technical initiatives involving extensive use of {', '.join(data['matched_skills'][:3])}.", styles['Normal']))
    story.append(Paragraph(f"• Collaborated with cross-functional teams to deliver high-impact system architectures.", styles['Normal']))
    story.append(Paragraph(f"• Optimized production workflows leading to significant improvements in reliability and performance.", styles['Normal']))
    story.append(Spacer(1, 15))

    # Education Placeholder
    story.append(Paragraph("EDUCATION", section_style))
    story.append(Paragraph("<b>Bachelor of Engineering in Computer Science</b>", styles['Normal']))
    story.append(Paragraph("National Institute of Technology | 2016 – 2020", styles['Normal']))
    
    doc.build(story)
    return resume_path

# ─────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────
@app.route('/', methods=['GET'])
def index():
    return send_file('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "SkillForge AI Backend"})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        resume_text = ""
        jd_text = request.form.get('job_description', '')
        user_name = request.form.get('user_name', 'Candidate')

        if 'resume' in request.files:
            file = request.files['resume']
            if file.filename.endswith('.pdf'):
                resume_text = extract_text_from_pdf(file)
            else:
                resume_text = file.read().decode('utf-8', errors='ignore')
        elif 'resume_text' in request.form:
            resume_text = request.form.get('resume_text', '')

        if not resume_text.strip():
            return jsonify({"error": "Resume text is empty or could not be extracted"}), 400
        if not jd_text.strip():
            return jsonify({"error": "Job description is required"}), 400

        result = analyze_resume_jd(resume_text, jd_text)
        result['user_name'] = user_name

        # Store for report generation
        session_id = str(uuid.uuid4())[:8]
        session_file = f"{UPLOAD_FOLDER}/session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump({
                "result": result,
                "resume_text": resume_text[:2000],
                "jd_text": jd_text[:2000],
                "user_name": user_name
            }, f)
        result['session_id'] = session_id

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/report/<session_id>', methods=['GET'])
@app.route('/api/report/<session_id>/<filename>', methods=['GET'])
def get_report(session_id, filename=None):
    try:
        session_file = f"{UPLOAD_FOLDER}/session_{session_id}.json"
        if not os.path.exists(session_file):
            return jsonify({"error": "Session not found"}), 404
        
        with open(session_file) as f:
            session_data = json.load(f)
        
        report_path = generate_pdf_report(
            session_data['result'],
            session_data['resume_text'],
            session_data['jd_text'],
            session_data['user_name']
        )
        
        return send_file(report_path, as_attachment=True,
                         download_name="SkillForge_Career_Report.pdf",
                         mimetype='application/pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-resume/<session_id>', methods=['GET'])
@app.route('/api/generate-resume/<session_id>/<filename>', methods=['GET'])
def get_standard_resume(session_id, filename=None):
    try:
        session_file = f"{UPLOAD_FOLDER}/session_{session_id}.json"
        if not os.path.exists(session_file):
            return jsonify({"error": "Session not found"}), 404
        
        with open(session_file) as f:
            session_data = json.load(f)
        
        resume_path = generate_standard_resume_pdf(
            session_data['result'],
            session_data['user_name']
        )
        
        return send_file(resume_path, as_attachment=True,
                         download_name=f"{session_data['user_name']}_Standard_Resume.pdf",
                         mimetype='application/pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-text', methods=['POST'])
def analyze_text():
    """For quick demo with plain text resume"""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        jd_text = data.get('job_description', '')
        user_name = data.get('user_name', 'Candidate')

        if not resume_text.strip() or not jd_text.strip():
            return jsonify({"error": "Both resume and job description are required"}), 400

        result = analyze_resume_jd(resume_text, jd_text)
        result['user_name'] = user_name

        session_id = str(uuid.uuid4())[:8]
        session_file = f"{UPLOAD_FOLDER}/session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump({
                "result": result,
                "resume_text": resume_text[:2000],
                "jd_text": jd_text[:2000],
                "user_name": user_name
            }, f)
        result['session_id'] = session_id

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower().strip()
        
        # Knowledge Base
        kb = {
            "analyze": "SkillForge AI uses a advanced neural matching engine based on TF-IDF vectorization and Cosine Similarity to compare your resume keywords with job description requirements. It doesn't just look for exact matches but understands domain relationships.",
            "skillgap": "The SkillGap Navigator identifies critical missing skills in your profile compared to the job market. For each gap, we provide a priority level, estimated time to master, and direct links to curated courses on YouTube, Coursera, and Kaggle.",
            "roadmap": "Our Career Roadmap is an AI-generated timeline that breaks down your upskilling journey into four phases: Foundation Building, Hands-On Practice, Skill Expansion, and Job Preparation. It gives you clear milestones to track your progress.",
            "score": "You can improve your resume score by adding quantifiable metrics (e.g., 'Increased revenue by 20%'), ensuring clinical keywords from the Job Description are present, and maintaining a professional structure with clear contact information.",
            "download": "You can download a comprehensive Career Intelligence Report in PDF format from the 'Analysis Results' page. We also offer a 'Standard Resume' generator that reformats your data into a professional, ATS-friendly template.",
            "jobs": "Yes! SkillForge AI helps you find jobs by generating direct search links to platforms like LinkedIn, Indeed, and Google Jobs, pre-filtered with the skills we've matched in your profile.",
            "who": "I am SkillForge AI, your dedicated Career Intelligence Assistant. I'm here to help you bridge the gap between your current skills and your dream career goals.",
            "creator": "SkillForge AI was architected by elite career strategists and AI engineers to democratize high-end career coaching."
        }

        # Simple intent matching
        response = ""
        if any(word in user_message for word in ["how", "analyze", "method", "work"]):
            response = kb["analyze"]
        elif any(word in user_message for word in ["gap", "navigator", "missing"]):
            response = kb["skillgap"]
        elif any(word in user_message for word in ["roadmap", "timeline", "journey", "plan"]):
            response = kb["roadmap"]
        elif any(word in user_message for word in ["score", "improve", "increase", "better"]):
            response = kb["score"]
        elif any(word in user_message for word in ["download", "report", "pdf", "save"]):
            response = kb["download"]
        elif any(word in user_message for word in ["job", "career", "search", "find"]):
            response = kb["jobs"]
        elif any(word in user_message for word in ["who", "what", "are you"]):
            response = kb["who"]
        elif any(word in user_message for word in ["creator", "made", "built"]):
            response = kb["creator"]
        else:
            response = "That's a great question! While I'm still learning, I can specifically help you with details about Resume Analysis, SkillGaps, Roadmaps, and Job Search. Ask me something like 'How can I improve my score?'"

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
