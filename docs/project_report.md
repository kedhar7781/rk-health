# RK Health – AI Smart Patient Portal & Medication Reminder Project Report

## 1. Executive Summary
RK Health is an intelligent, patient-centric web application designed to optimize healthcare organization for individuals. By fusing modern dashboard engineering, lightweight offline storage (SQLite), real-time Google Calendar scheduling, Google Sheets cloud storage synchronization, Twilio SMS alerts, and generative AI summarization, RK Health delivers an all-in-one assistant for clinical scheduling and medication compliance.

---

## 2. Problem Statement
Patients tracking complex medical treatments often struggle with:
1. **Adherence Failures**: Forgetting pill timings or doses.
2. **Scheduling Disconnects**: Missing doctor consultations or failing to integrate appointments into their primary digital calendars (e.g. Google Calendar).
3. **Medical Information Overload**: Interpreting clinical terminology (such as "ECG", "Cardiovascular", specific drug names like "Lisinopril") or tracking medical changes across disparate logs.
4. **Poor Log Retention**: Keeping unstructured notes regarding symptoms and side-effects.

---

## 3. Solution Overview
RK Health resolves these difficulties by creating an integrated ecosystem:
- **Medication Regimen Tracker**: Allows patients to schedule pills, log dosage volumes, set daily times, track compliance status (Active, Paused, Completed), and send SMS text alerts.
- **Smart Appointment Scheduler**: Logs patient/doctor schedules, syncs them to Google Sheets as a database, and creates Calendar invites.
- **Digital Health Diary**: Stores qualitative journals tracking symptom progressions.
- **AI Summary Analyst**: Synthesizes structured data logs into plain-language Markdown reports, outlining daily regimens, explaining complex medical jargon, and suggesting preventative tips.

---

## 4. Tech Stack & Integration Rationale
1. **Frontend**: Pure HTML5, CSS3 Variables, and vanilla JavaScript. Avoids heavy frameworks to ensure sub-100ms client rendering speeds. FontAwesome provides clinical iconography. Chart.js powers dashboard analytics.
2. **Backend**: Flask (Python) with JWT-like Session security. Chosen for its micro-framework footprint, ease of routing static content, and compatibility with standard Python databases.
3. **Cloud Synchronization**: A Google Apps Script Web App coordinates Sheets and Calendar operations. This avoids distributing private Google OAuth credentials to client browsers or local servers, wrapping interactions in an Apps Script execution context.
4. **Twilio SMS Platform**: Direct programmatic SMS dispatcher utilizing E.164 phone formats.
5. **AI Summarization Gateway**: Integrates with OpenAI compatible endpoints (Grok, Llama, ChatGPT).

---

## 5. Security & Data Management
- **Password Security**: Credentials are encrypted using PBKDF2 with a SHA256 HMAC algorithm (salted iterations) prior to database insertion.
- **Session Protection**: Flask sessions use cryptographic secrets to verify client identities.
- **Transactional integrity**: Database connections implement transactions (`commit` and `rollback`) to ensure local SQLite operations are not left in partial states on error.

---

## 6. Implementation Challenges & Mitigations
- **Network Latency & Offline Integrity**: External API calls to Google Sheets, Calendars, or Twilio introduce network lag (up to several seconds).
  - *Mitigation*: The Flask backend immediately commits entries to the local SQLite database. External network operations are run safely, and in the event of external outages, the server logs warning states, allowing local operation without blocking the patient dashboard.
- **Mobile Responsive Tables**: Multi-column patient logs easily clip on mobile displays.
  - *Mitigation*: Custom CSS tables use horizontal scrolling wrappers and badge icons to replace verbose texts in small viewports.

---

## 7. Future Roadmap
1. **AI Chatbot**: Add a conversational assistant to answer questions about medications in real-time.
2. **Wearable Integrations**: Sync heart rate and step logs from Apple HealthKit or Fitbit.
3. **Smart Scheduling**: Let patients input doctor availability files, suggesting optimal slots using matching algorithms.
