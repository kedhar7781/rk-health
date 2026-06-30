import requests
import logging
import json
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def generate_ai_summary(appointments, medications, notes):
        """
        Sends the compiled clinical data to an OpenAI-compatible API to generate:
        1. Patient Visit Summary
        2. Medicine Instructions
        3. Follow-up Advice
        4. Health & Wellness Tips
        5. Patient-friendly explanations of complex terms
        """
        api_key = Config.AI_API_KEY
        api_base = Config.AI_API_BASE
        model = Config.AI_MODEL
        
        # Compile clinical context
        context = "CLIENT HEALTH RECORD DATA:\n\n"
        context += "--- Appointments ---\n"
        for a in appointments:
            context += f"- Date: {a['appointment_date']} at {a['appointment_time']}, Dr. {a['doctor_name']}. Notes: {a['notes']}\n"
            
        context += "\n--- Medications ---\n"
        for m in medications:
            context += f"- Med: {m['medicine_name']}, Dosage: {m['dosage']}, Frequency: {m['frequency']}, Time: {m['reminder_time']}, Status: {m['status']}\n"
            
        context += "\n--- Patient Health Notes ---\n"
        for n in notes:
            context += f"- Note Title: {n['title']}. Content: {n['content']}\n"

        prompt = f"""
You are RK Health AI, a highly empathetic and knowledgeable clinical assistant.
Your task is to analyze the patient's health data below and generate a friendly, professional, and clear health report summary.

{context}

Please structure your response exactly with the following five sections, using clear Markdown headings:

# Patient Visit Summary
Summarize the current visits and key notes in a friendly, conversational manner. Explain what the doctor visits indicate about their health.

# Medicine Instructions
Review their active medications. Explain what each medicine does, when to take it, and how it fits into their routine. If there are completed medicines (e.g. Amoxicillin), mention that they have finished their course.

# Follow-up Advice
Outline what the patient needs to do next (e.g., schedule appointments, get checkups, monitor symptoms).

# Health & Wellness Tips
Provide 3 tailored lifestyle tips based on their health notes (e.g., limit caffeine if palpitations are mentioned, take light walks, stay hydrated).

# Patient-Friendly Medical Explanations
Translate any clinical terms used (e.g. 'ECG', 'Cardiovascular', 'palpitations', 'Lisinopril', 'dermatologist') into simple, easy-to-understand language.

Ensure the tone is warm, encouraging, and clear. Avoid complex jargon without explaining it.
"""

        if not api_key:
            logger.warning("AI_API_KEY not configured. Falling back to the rule-based mock engine.")
            return AIService._generate_mock_summary(appointments, medications, notes)

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful and expert clinical summarizer."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            url = f"{api_base.rstrip('/')}/chat/completions"
            response = requests.post(url, headers=headers, json=data, timeout=20)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"AI API returned status code {response.status_code}: {response.text}")
                return f"Error from AI Engine (Code {response.status_code}). Falling back to local summarizer:\n\n" + AIService._generate_mock_summary(appointments, medications, notes)
                
        except Exception as e:
            logger.exception("AI generation request failed")
            return f"Failed to connect to AI server. Showing local compiled summary:\n\n" + AIService._generate_mock_summary(appointments, medications, notes)

    @staticmethod
    def _generate_mock_summary(appointments, medications, notes):
        """
        Fallback system that analyzes data rules-based and compiles a rich Markdown response.
        """
        # Patient Visit Summary
        visit_summary = "You currently have appointment schedules with "
        doctors = [a['doctor_name'] for a in appointments]
        if doctors:
            visit_summary += ", and ".join(list(set(doctors))) + "."
        else:
            visit_summary += "no doctors registered recently."
        
        # Medicine Instructions
        med_instr = ""
        active_meds = [m for m in medications if m['status'].lower() == 'active']
        completed_meds = [m for m in medications if m['status'].lower() == 'completed']
        
        if active_meds:
            med_instr += "### Active Medications:\n"
            for m in active_meds:
                med_instr += f"- **{m['medicine_name']} ({m['dosage']})**: Take {m['frequency'].lower()} at {m['reminder_time']}. Ensure you do not skip doses.\n"
        if completed_meds:
            med_instr += "\n### Completed Course:\n"
            for m in completed_meds:
                med_instr += f"- **{m['medicine_name']} ({m['dosage']})**: Course completed. If symptoms return, contact your physician.\n"
        if not active_meds and not completed_meds:
            med_instr = "No medications scheduled on record."

        # Follow-up advice
        follow_up = ""
        if appointments:
            for a in appointments:
                follow_up += f"- Keep your appointment on **{a['appointment_date']}** at **{a['appointment_time']}** with **{a['doctor_name']}**. Note: *{a['notes']}*\n"
        else:
            follow_up = "- No upcoming doctor visits are currently scheduled. Consider scheduling a routine annual checkup."

        # Health Tips
        tips = [
            "- **Track Symptoms Daily**: Keep a close log of physical symptoms such as blood pressure or skin rashes to share with your physicians.",
            "- **Maintain Medication Consistency**: Set your smart notifications active. Taking medicines at consistent hours improves therapeutic efficacy.",
            "- **Hydration & Sleep**: Drink at least 8 glasses of water daily and target 7-8 hours of sleep to support overall recovery."
        ]
        
        # Check notes for specific conditions to tailor tips
        notes_content = " ".join([n['content'].lower() for n in notes])
        if "caffeine" in notes_content or "palpitation" in notes_content or "cardio" in notes_content:
            tips.insert(0, "- **Manage Stimulants**: Since palpitations or cardiovascular events were monitored, reduce coffee, energy drinks, and tea. Substitute with herbal alternatives.")
            tips.pop()
        if "rash" in notes_content or "dermatologist" in notes_content:
            tips.insert(1, "- **Skin Hydration**: Avoid long hot showers. Use gentle, non-scented moisturizers twice daily on areas affected by rashes.")

        # Definitions
        explanations = """
- **ECG (Electrocardiogram)**: A quick test that records the electrical signals of your heart to monitor cardiovascular health.
- **Cardiologist**: A specialized doctor focusing on diagnosing and treating diseases of the heart and blood vessels.
- **Lisinopril**: A prescription medication commonly used to treat high blood pressure and prevent heart attacks.
- **Dermatologist**: A doctor specializing in treating skin, hair, and nail disorders.
"""

        tips_str = "\n".join(tips)
        mock_md = f"""# Patient Visit Summary
{visit_summary}
Based on your health records, you are tracking your symptoms and maintaining consultations. It is recommended to log your vital readings (like blood pressure or skin progress) leading up to your consultations.

# Medicine Instructions
{med_instr}

# Follow-up Advice
{follow_up}
- Bring an updated list of your symptoms and medication logs to your next consult.

# Health & Wellness Tips
{tips_str}

# Patient-Friendly Medical Explanations
{explanations}
"""
        return mock_md
