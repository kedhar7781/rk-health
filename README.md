# RK Health – AI Smart Patient Appointment & Medication Reminder System

RK Health is an intelligent, patient-centric web portal that empowers patients to manage doctor appointments, schedule medication regimens, maintain health symptom logs, and receive AI-generated clinical advice.

---

## 🌟 Key Features

- **📊 Patient Dashboard**: Responsive grid layout featuring Chart.js health summaries, daily compliance status widgets, and upcoming appointment timelines.
- **📅 Appointment Scheduler**: Book, edit, and cancel appointments with automated synchronization to **Google Sheets Database** and **Google Calendar events**.
- **💊 Medication Regimen Tracker**: Configure medicine names, dosage volumes, exact reminder times, and frequency intervals (e.g. daily, as needed).
- **💬 Twilio SMS Alerts**: Sends immediate reminders and confirmations to patient phones. Supports local sandboxed logger falls-backs on sandbox environment.
- **📝 Patient Health Diary**: Record symptoms, vital metrics, and observations to share with clinical practitioners.
- **🧠 Generative AI Assistant**: Analyzes patient datasets and utilizes Grok/Llama/OpenAI models to translate complex medical terms, generate visit instructions, and outline preventative wellness tips.
- **🎨 Glassmorphic Theme Design**: Features custom CSS variables supporting dark/light mode toggles, micro-animations, slide-in toasts, and custom fonts.
- **🖨️ Print Optimization**: Custom print styles to export AI health reports directly to paper or PDF files.

---

## 🏗️ Project Architecture & Stack

```
                  +-----------------------------------+
                  |           Patient Web UI          |
                  |     (HTML5, Premium CSS3, JS)     |
                  +-----------------+-----------------+
                                    |
                                    | (REST APIs / JSON)
                                    v
                  +-----------------------------------+
                  |           Flask Backend           |
                  +-----+-----------+-----------+-----+
                        |           |           |
       (Local SQLite)   |           |           | (OpenAI / Grok / Llama API)
                        v           v           v
             +------------+   +-----------+   +-------------+
             | SQLite DB  |   |  Twilio   |   | AI Summary  |
             | (Vitals /  |   |  SMS Gate |   | Engine      |
             |  Schedules|   +-----------+   +-------------+
             +------------+
                        |
                        | (Forward/Push REST payload)
                        v
         +---------------------------------------------+
         |      Google Apps Script REST Web App        |
         +----------------------+----------------------+
                                |
                   +------------+------------+
                   |                         |
                   v                         v
         +-------------------+     +--------------------+
         |   Google Sheets   |     |   Google Calendar  |
         | (Cloud Database)  |     | (Appointment Sync) |
         +-------------------+     +--------------------+
```

- **Frontend**: HTML5, Vanilla CSS3, Javascript, FontAwesome icons, Chart.js.
- **Backend**: Flask (Python 3.10), SQLite3.
- **Integrations**: Twilio SMS REST Client, Google Apps Script Web App, OpenAI Chat Completions API.

---

## 📂 Project Structure

```
├── backend/
│   ├── app.py                # Flask main entrypoint
│   ├── config.py             # Environment configurations manual loader
│   ├── database.py           # SQLite setup and mock dataset seeds
│   ├── routes/               # API blueprints (auth, appointments, meds, notes, summary)
│   ├── services/             # Integrations (ai_service, google_service, twilio_service)
│   └── tests/                # Pytest automation suite (auth, appts, meds, notes)
├── docs/                     # Documentation files
│   ├── architecture.md       # Topological system blueprints
│   ├── api_docs.md           # API request/response documentation
│   ├── setup_guide.md        # Credentials & third-party setup instructions
│   ├── project_report.md     # Detailed engineering summary
│   └── presentation.html     # Interactive slide deck presentation
├── frontend/                 # Client assets
│   ├── index.html            # Dashboard layout
│   ├── login.html            # Portal login
│   ├── register.html         # Portal registration
│   ├── css/styles.css        # Premium style layouts & theme styles
│   └── js/                   # Core controllers (app.js, auth.js)
├── google-apps-script/       # Sheets & Calendar script bridge code.js
├── .env.example              # Credentials configurations template
├── .gitignore                # Source control filters
├── Dockerfile                # Image container configuration
├── docker-compose.yml        # Multi-container orchestrator
├── requirements.txt          # Python dependencies
└── README.md                 # Entry manual
```

---

## 🚀 Quick Start Instructions

1. **Configure Environment Keys**:
   Copy `.env.example` to `.env` and fill in API keys:
   ```bash
   cp .env.example .env
   ```
   *Note: If no keys are provided, AI and Twilio will fall back to local mock compiling simulation logs so the app remains fully testable.*

2. **Launch with Docker**:
   ```bash
   docker-compose up --build
   ```
   Open `http://localhost:5000` in your web browser.

3. **Or Launch Locally (Python)**:
   ```bash
   python -m venv venv
   # Activate: .\venv\Scripts\activate (Windows) or source venv/bin/activate (macOS/Linux)
   pip install -r requirements.txt
   python backend/app.py
   ```
   Open `http://localhost:5000` in your web browser.

4. **Access Portal Demo User**:
   The system initializes SQLite database with seed records:
   - **Username**: `admin`
   - **Password**: `admin123`

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
