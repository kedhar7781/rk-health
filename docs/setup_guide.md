# RK Health - Setup & Deployment Guide

This guide will lead you through setting up, configuring, and deploying the **RK Health – AI Smart Patient Appointment & Medication Reminder System** from scratch.

---

## 1. Local Development Setup

### Prerequisites
- Python 3.10 or higher
- Node.js (Optional, for deploying frontend separately)
- SQLite3 (Preinstalled on most modern OS)

### Installation
1. Clone the project repository or navigate to the workspace.
2. Initialize virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate virtual environment:
   - **Windows PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
4. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy configuration environment file:
   ```bash
   copy .env.example .env
   ```
6. Spin up Flask server:
   ```bash
   python backend/app.py
   ```
7. Open a browser and visit: `http://localhost:5000`

> [!NOTE]
> The database initialized on start will automatically seed a mock profile:
> - **Username**: `admin`
> - **Password**: `admin123`
> This allows you to explore the dashboard immediately without registering.

---

## 2. Google Apps Script Configuration (Sheets & Calendar)

To sync appointments with Google Calendar and save records directly to Google Sheets database, deploy the script bridge:

1. Open [Google Sheets](https://sheets.google.com). Create a new blank spreadsheet.
2. Under **Extensions**, select **Apps Script**.
3. Clear the default template code in `Code.gs` and paste the contents of [code.js](file:///C:/Users/matse/.gemini/antigravity/scratch/rk-health/google-apps-script/code.js).
4. Save the project (click the floppy disk icon).
5. Deploy the script as a Web App:
   - Click **Deploy** -> **New deployment**.
   - Select **Web app** as the deployment type.
   - Set **Execute as**: `Me (your-email@gmail.com)`.
   - Set **Who has access**: `Anyone`.
   - Click **Deploy**.
6. Google will request you to authorize permissions. Click **Authorize access**, choose your account, click **Advanced** -> **Go to Untitled Project (unsafe)**, and click **Allow**.
7. Copy the **Web App URL** provided under the deployment details page.
8. Open your local `.env` file and set the value of `GOOGLE_APPS_SCRIPT_URL`:
   ```env
   GOOGLE_APPS_SCRIPT_URL=https://script.google.com/macros/s/xxxxxx-yyyyyy/exec
   ```
9. Restart your Flask server. Appointments and medications will now automatically sync to Google Sheets tabs and your default Google Calendar!

---

## 3. Twilio SMS Configuration

To receive immediate SMS text confirmations and medication alerts on your phone:

1. Sign up or log into the [Twilio Console](https://www.twilio.com/console).
2. Create a project and obtain a **Twilio Phone Number**.
3. Under the Account Dashboard page, copy the **Account SID** and **Auth Token**.
4. Set these variables in your `.env` file:
   ```env
   TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   TWILIO_AUTH_TOKEN=your_secret_auth_token
   TWILIO_PHONE_NUMBER=+15551234567
   ```
5. Log into the RK Health Patient portal, go to Registration or update your user profile, and ensure your phone number matches the **E.164** format (e.g. `+14155552671` including country code).
6. Save medication schedules or appointments checking the SMS alert checkbox to receive automated notifications.

---

## 4. Grok / Llama / OpenAI compatible AI Configuration

To generate patient visit summaries and preventative guidelines:

1. Obtain an API Key from your preferred AI vendor (OpenAI, xAI/Grok, Perplexity, OpenRouter, or local Ollama).
2. Configure the API endpoint and model inside the `.env` file:
   ```env
   AI_API_KEY=sk-proj-xxxxxxxxxxxx
   AI_API_BASE=https://api.openai.com/v1
   AI_MODEL=gpt-3.5-turbo
   ```
3. Navigate to the **AI Health Report** tab on the sidebar and click **Generate AI Summary** to request reports.

---

## 5. Docker Deployment

To launch the app containerized:

1. Build and run containers using Docker Compose:
   ```bash
   docker-compose up --build -d
   ```
2. Verify container logs:
   ```bash
   docker-compose logs -f rk-health-app
   ```
3. Access portal at: `http://localhost:5000`

---

## 6. Cloud Platform Deployments

### Render / Railway (Backend + API + Static Web Server)
1. Fork your RK Health repository to your personal GitHub account.
2. Link your repository to a new **Web Service** on Render.
3. Configure settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend/app.py`
4. Add all required keys from `.env.example` to **Environment Variables** settings under Render Dashboard.
5. Deploy. Render will serve the APIs and host the static files on its domain.

### GitHub Pages (Frontend Hosting Only)
If you wish to host the frontend separately on GitHub Pages:
1. Update `app.js` API fetch endpoints to point to the absolute URL of your deployed Render/Railway backend server instead of relative paths (e.g. change `/api/auth` to `https://rk-health-backend.onrender.com/api/auth`).
2. Add a `gh-pages` deployment action or commit the `frontend` folder directly to a `gh-pages` branch.
3. Configure settings under repository settings to host from branch.
