# 💬 WhatsApp Loan Tracker

A WhatsApp-based EMI Loan Tracker built with **FastAPI**, **SQLAlchemy**, **Twilio WhatsApp API**, and **SQLite**.

The application allows borrowers and lenders to manage loans directly from WhatsApp without requiring a separate mobile app or web dashboard.

---

# ✨ Features

- 📄 Create a new loan
- 📅 Automatic EMI schedule generation
- 💰 Record EMI payments
- 🔄 Supports partial payments
- 📊 Real-time loan status
- 📨 WhatsApp notifications to borrower & lender
- 🔔 Monthly EMI reminder (Cloud Scheduled)
- 🔐 Secure Internal Reminder API
- ⚙️ Environment-based configuration
- 🚀 Ready for Railway deployment

---

# 📱 Supported WhatsApp Commands

| Command | Description |
|----------|-------------|
| STATUS | Show current loan status |
| PAY 3000 | Record EMI payment |
| DEBUG LOAN | Display loan information (Development only) |

---

# 🏗️ System Architecture

```text
                  WhatsApp

                      │

                      ▼

              FastAPI Webhooks

                      │

        ┌─────────────┴─────────────┐

        ▼                           ▼

 Loan Services             Reminder Services

        │                           ▲

        │                           │

        ▼                    Railway Cron

               SQLAlchemy ORM

                      │

                      ▼

                   SQLite

                      │

                      ▼

             Twilio WhatsApp API
```

---

# 🛠️ Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- Twilio WhatsApp API
- Uvicorn
- Railway
- GitHub

---

# 📂 Project Structure

```text
WhatsappEMIBot/

│

├── app.py

├── config.py

├── database.py

├── send_reminders.py

├── requirements.txt

│

├── models/

├── routes/

├── schemas/

├── services/

│

├── data/

│

└── README.md
```

---

# 🚀 Local Setup

Clone the repository

```bash
git clone https://github.com/<YOUR_USERNAME>/whatsapp-loan-tracker.git
```

Go inside the project

```bash
cd whatsapp-loan-tracker
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```text
TWILIO_ACCOUNT_SID=

TWILIO_AUTH_TOKEN=

TWILIO_WHATSAPP_NUMBER=

INTERNAL_API_KEY=

DATABASE_URL=sqlite:///data/emi.db
```

Run the application

```bash
uvicorn app:app --reload
```

---

# 🔔 Monthly Reminder Flow

Every month Railway Cron invokes

```text
POST /internal/send-reminders
```

↓

The Reminder Service

↓

Calculates outstanding EMIs

↓

Sends reminder to

- Borrower
- Lender

via WhatsApp.

---

# 🔒 Security

- Internal reminder endpoint protected using API Key
- Environment variables stored outside source code
- Sensitive files excluded using `.gitignore`

---

# 🌱 Future Enhancements

- Loan Closure Notification
- Payment History
- Admin Dashboard
- PostgreSQL Support
- OCR-based Payment Verification
- UPI Integration
- PDF Statement Generation

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Subhojit Bhattacharjee**

Automation QA Engineer | Python | FastAPI | Playwright | Selenium | API Testing