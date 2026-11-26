# ⚡ SkillForge AI — Career Intelligence Platform

> Intelligent Resume Analyzer & Career Roadmap System  
> Full-Stack AI SaaS Web Application  
> Built with Python, Flask & Modern Frontend Technologies

---

## 🏗️ Architecture

```
skillforge/
├── backend/
│   └── app.py          ← Flask REST API + AI Engine
├── frontend/
│   └── index.html      ← Full SPA (HTML/CSS/JS)
├── uploads/            ← Temporary session storage
├── reports/            ← Generated PDF reports
└── start.sh            ← One-command startup
```

---

## 🧠 AI Models Used

| Model | Purpose |
|-------|---------|
| **TF-IDF Vectorizer** | Text feature extraction |
| **Cosine Similarity** | Resume ↔ JD match scoring |
| **Regex NLP Engine** | Skill extraction from text |
| **Custom Scoring Engine** | Resume quality scoring (0-100) |
| **Role Prediction Engine** | Career role classification |
| **Gap Analysis Engine** | Missing skill prioritization |

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install flask flask-cors scikit-learn PyPDF2 reportlab
```

### Run the App
```bash
bash /home/claude/skillforge/start.sh
```

Then open `frontend/index.html` in your browser.

### Demo Login
- **Email:** demo@skillforge.ai  
- **Password:** demo1234

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/analyze` | Analyze PDF resume + JD |
| POST | `/api/analyze-text` | Analyze text resume + JD |
| GET | `/api/report/<session_id>` | Download PDF report |

### Example API Call
```bash
curl -X POST http://localhost:5000/api/analyze-text \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python developer with ML experience...",
    "job_description": "Looking for Senior Data Scientist...",
    "user_name": "John Smith"
  }'
```

---

## 🎨 Pages & Features

### 1. 🏠 Dashboard (Home)
- Drag & drop PDF resume upload
- Text paste option
- Job description input
- AI Analyze button
- Demo data loader

### 2. 📊 Analysis Results
- Match % score with color coding
- Resume quality score (0-100)
- AI-predicted job role
- Experience level detection
- Matched / Missing / Extra skills (color tags)
- 3 interactive Chart.js graphs:
  - Doughnut: Skill match overview
  - Radar: Domain strength
  - Bar: Skill gap priorities
- AI Insights Panel (strengths, weaknesses, suggestions)
- Time-to-job-ready prediction
- Keyword optimization progress bars

### 3. 🎯 SkillGap Navigator
- Cards for each missing skill
- Why the skill matters
- Difficulty & Priority badges
- Direct links: YouTube, Coursera, Kaggle
- Project idea per skill

### 4. 🗺️ CareerForge Roadmap
- Visual timeline with phases
- Milestones per phase
- Skill completion tracker
- Target role display

### 5. 📚 Learning Intelligence Hub
- Curated resources per skill
- YouTube tutorials
- Course links (Coursera, AWS, Udemy)
- Kaggle practice datasets
- Project ideas
- 7-day daily learning plan

### 6. ⬇️ PDF Report Download
- Professional PDF via ReportLab
- Score cards, insights, skills
- Career roadmap
- Clean modern design

---

## 🛠️ Production Upgrade Path

To make this fully production-ready, add:

1. **Supabase Auth** — Replace localStorage login with Supabase
2. **PostgreSQL** — Store user sessions & history  
3. **sentence-transformers** — For semantic skill matching (when space allows)
4. **spaCy NLP** — Advanced text parsing
5. **Redis** — Session caching
6. **Nginx** — Reverse proxy for frontend
7. **Docker** — Containerize frontend + backend
8. **Vercel/Netlify** — Frontend deployment
9. **Railway/Render** — Backend deployment

---

## 🔐 Authentication Flow

Currently uses localStorage for demo purposes.  
For production: integrate Supabase with these steps:
```javascript
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
const { data, error } = await supabase.auth.signInWithPassword({email, password})
```

---

## 📦 Requirements

```
flask>=3.0.0
flask-cors>=4.0.0
scikit-learn>=1.4.0
PyPDF2>=3.0.0
reportlab>=4.0.0
```

---

*Built with ❤️ — SkillForge AI Career Intelligence Platform*
