# KOI LMS — AI-Driven Learning Management System

An educational Learning Management System (LMS) extended with an AI Query Engine to help students with assignment deadlines, grades, course content, exam schedules and general queries.

---

**Project summary**

- A Django-based LMS with two main apps: `adminapp` (administration tools) and `lms_core` (student-facing LMS features).
- Integrated simple, local AI assistant (`lms_core.ai_engine.AIQueryEngine`) that:
  - Detects intent using keyword matching
  - Extracts simple entities (course codes, assignment numbers)
  - Answers assignment/grade/exam queries by querying the database
  - Uses TF–IDF + cosine similarity over `KnowledgeBase` items fo8r general queries
- Includes management commands to import sample CSV data and create student profiles.

**Key features**

- Student authentication and profiles
- Dashboard with GPA/statistics calculations
- Course pages with assignments, quizzes and forums
- Grades and grade analytics per course
- AI-powered query interface (`/ai-query/`) and an API view implemented (`api_query`) for programmatic queries
- Data seeding commands: `import_data` and `create_student_profiles`

---

**Quick start**

Prerequisites:

- Python 3.10+ (development environment shows Python 3.14)
- pip

Install & run locally:

```bash
# create & activate venv (Windows)
python -m venv env
env\Scripts\activate

# install requirements
pip install -r lms/requirements.txt

# apply migrations
python lms/manage.py migrate

# import sample data (optional)
python lms/manage.py import_data
python lms/manage.py create_student_profiles

# create admin user
python lms/manage.py createsuperuser

# run server
python lms/manage.py runserver
```

Open: http://127.0.0.1:8000/ (student flows) and http://127.0.0.1:8000/admin/ (Django admin)

---

**AI Query usage**

- Web UI: visit `/ai-query/` after logging in as a student.
- API (view implemented in `lms_core.views.api_query`): POST JSON `{"query": "..."}`. Note: the API view exists but may not be exposed by default in `urls.py`; if you want an API route, add a URL entry such as:

```python
# in lms_core/urls.py
path('api/ai-query/', views.api_query, name='api_ai_query')
```

Example curl (after adding the URL if needed):

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "When is the COMP101 final exam?"}' \
  http://127.0.0.1:8000/api/ai-query/
```

**AI internals (short)**

- Class: `lms_core.ai_engine.AIQueryEngine`
- Intent detection: keyword counts across predefined categories
- Entity extraction: regex-based (course codes like COMP101, assignment numbers)
- Response generation: uses DB models (`Course`, `Assignment`, `Grade`, `Quiz`, `KnowledgeBase`) to build answers or uses TF–IDF similarity on knowledge base items

---

**Project structure (important files & folders)**

```
koi-lms/
├─ data/                     # CSV/JSON sample dataset (students, grades, quizzes...)
├─ env/                      # virtualenv recorded in the repo for convenience
├─ lms/                      # main Django project
│  ├─ lms/                   # project settings, urls, wsgi/asgi
│  ├─ lms_core/              # core app: models, views, AI engine, templates
│  │  ├─ ai_engine.py        # AI logic (TF-IDF, handlers, intents)
│  │  ├─ management/commands # import_data, create_student_profiles
│  │  ├─ templates/          # HTML templates (dashboard, ai_query etc.)
│  │  └─ static/             # static assets
│  └─ adminapp/              # admin-facing CRUD views & templates
└─ README.md
```

**Project Structure Diagram**

_Add a diagram to `docs/structure.png` or `docs/architecture.png`, then update the link below to show the image in this README._

![Project structure diagram](docs/structure.png)

Or use an external link:

[Project structure image](https://example.com/your-structure-diagram.png)

---

**Development notes & tips**

- The AI engine is intentionally lightweight and runs entirely on the server using scikit-learn — no external cloud LLMs are required.
- KnowledgeBase items (model `KnowledgeBase`) are used as FAQs to answer general queries via similarity matching.
- Logging and error handling are basic; consider adding proper logging, tests and input sanitization for production use.

**Contributing**

- Feel free to open an issue or pull request. For major changes (e.g., replacing the AI backend with a remote LLM), open an issue first to discuss design.

**License**

- Add your preferred license here (e.g., MIT) or keep it internal for now.

**Maintainers / Contact**

- Project maintained by the KOI LMS team.
- For questions, reach the repository owner or the project's internal contact.

---

If you'd like, I can:
- add the `api/ai-query` URL to `lms_core/urls.py` so the API is reachable
- add a small architecture SVG/PNG under `docs/` and update the image link
- create a short CONTRIBUTING.md template

Which of these would you like me to do next?