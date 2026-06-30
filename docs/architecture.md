# RK Health - System Architecture

RK Health is designed with a hybrid client-server topology that couples a local Flask (Python) server with Google Cloud microservices (Sheets Database & Calendar Events) and Twilio SMS notification. This architecture ensures high local developer productivity while maintaining production integrations.

## Architecture Topology

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

## System Components

### 1. Web Portal Frontend
- **Design Philosophy**: Glassmorphic dark/light hybrid theme utilizing native CSS custom variables. Responsive layout built on flexbox and grid systems. Responsive sidebar with automatic collapsible menu toggler for mobile viewport support.
- **Engine Logic**: Pure client-side JS (`app.js`, `auth.js`) managing active view state, session checks, forms collection, Chart.js renderings, pagination limits, and toast alerting.
- **Data Rendering**: Employs a custom regular-expression-based markdown compiler that converts AI summaries into formatted HTML views.

### 2. Flask API Server
- **Core App**: Built on Flask (`app.py`), configured for cross-origin resource sharing (CORS), serving frontend assets, and bootstrapping initial SQLite DB tables.
- **Blueprints**: Modularity achieved via resource-specific blueprints:
  - `/api/auth`: Patient registration and password hashing using PBKDF2 cryptography.
  - `/api/appointments`: Search, date-range checks, and local database CRUD operations synced to Google services.
  - `/api/medications`: Patient medication regimens, scheduling reminders, and manual SMS tester hooks.
  - `/api/notes`: Health observation records.
  - `/api/summary`: Custom dashboard statistics compiler and OpenAI-compatible client.

### 3. SQLite Database Layer
Acts as the immediate data sink for local deployments.
- **`users`**: Manages credentials, contact emails, and target SMS numbers.
- **`appointments`**: Logs patient name, doctor, scheduled timestamp, notes, and the calendar sync event reference.
- **`medications`**: Tracks medicine name, dosage, frequency intervals, scheduled alert times, status (Active/Completed/Paused), and Twilio subscription state.
- **`health_notes`**: Logs user-defined text records (symptoms, doctor comments, side-effects).

### 4. Google Apps Script Web App Bridge
- **Purpose**: Deploys directly to the patient's Google Drive. Acts as an API gateway that enables the Flask server to interact with Google Sheets and Google Calendar securely without managing complex Google Cloud OAuth 2.0 developer client configurations on the local server.
- **Functions**: Handles POST payloads dynamically. Creates default spreadsheets, logs rows, updates fields, removes rows, and manages Calendar events using Google Script services (`SpreadsheetApp` and `CalendarApp`).

### 5. Twilio SMS Service
- **Functions**: Performs E.164 verification checks. Validates phone configuration prior to scheduling notifications. Integrates template text configurations.
- **Developer Fallback**: Outputs SMS bodies directly to the Python console logger if credentials are not specified in the environment variables, maintaining end-to-end sandbox continuity.

### 6. AI Summarization Gateway
- **Format**: Interfaces with any OpenAI-compatible API gateway (OpenAI, Grok, Llama).
- **Fallback**: Compiles standard template advice based on rules checking patient vitals and logs if the gateway key is omitted.
