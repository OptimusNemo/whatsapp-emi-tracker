# 💬 WhatsApp Loan Tracker

A WhatsApp-based EMI Loan Tracker built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, **Twilio WhatsApp API**, and **Railway**.

The application allows borrowers and lenders to manage loans directly from WhatsApp without requiring a separate mobile app or web dashboard.

---

# ✨ Features

- 📄 Create a new loan
- 📅 Automatic EMI schedule generation
- 💰 Record EMI payments
- 🔄 Supports partial payments
- 📊 Real-time loan status
- 📨 WhatsApp notifications to borrower & lender
- 🔔 Automated monthly EMI reminders
- ♻️ Idempotent reminders to prevent duplicate notifications
- 🔐 Secure internal reminder API protected by API key
- ⏰ Dedicated Railway Cron service for monthly reminders
- 🗄️ PostgreSQL production database
- 🔄 SQLite → PostgreSQL migration support
- ⚙️ Environment-based configuration
- 🚀 Production deployment on Railway

---

# 📱 Supported WhatsApp Commands

| Command | Description |
|----------|-------------|
| `STATUS` | Show current loan status |
| `PAY 3000` | Record an EMI payment |
| `DEBUG LOAN` | Display loan information (Development only) |

> Replace `3000` with the actual payment amount when recording a payment.

---

# 🏗️ System Architecture

```text
                         WhatsApp
                            │
                            ▼
                    Twilio WhatsApp API
                            │
                            ▼
                    FastAPI Webhooks
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       Loan / Payment Services      Reminder Service
              │                           │
              │                           ▼
              │                    Railway Cron
              │                           │
              └──────────────┬────────────┘
                             ▼
                       SQLAlchemy ORM
                             │
                             ▼
                        PostgreSQL
```

## Monthly Reminder Flow

```text
Railway Cron
     │
     ▼
POST /internal/send-reminders
     │
     ▼
Reminder Service
     │
     ├── Check reminder log for loan + date
     │
     ├── Already sent?
     │      └── YES → Skip
     │
     └── NO
          │
          ├── Find next pending EMI
          ├── Calculate outstanding amount
          ├── Send WhatsApp to borrower
          ├── Send WhatsApp to lender
          └── Mark reminder as sent
```

The reminder process is **idempotent**. Re-running the reminder job on the same date does not send another reminder for the same loan.

---

# 🛠️ Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Twilio WhatsApp API
- Uvicorn
- Railway
- Railway Cron
- GitHub

---

# 📂 Project Structure

```text
WhatsappEMIBot/
│
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── README.md
│
├── models/
│   ├── loan.py
│   ├── emi.py
│   ├── payment.py
│   └── reminder_log.py
│
├── routes/
│   ├── whatsapp.py
│   └── internal.py
│
├── schemas/
│
├── services/
│   ├── loan_service.py
│   ├── payment_service.py
│   ├── reminder_service.py
│   └── notification_service.py
│
├── migrate_sqlite_to_postgres.py
│
├── data/
│
└── README.md
```

Development/test helper scripts such as `reset_loan.py` and `verify_loan.py` may be kept locally for database testing and verification. They are not required by the production runtime.

---

# 🚀 Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/<YOUR_USERNAME>/whatsapp-emi-tracker.git
```

## 2. Go inside the project

```bash
cd whatsapp-emi-tracker
```

## 3. Create a virtual environment

```bash
python -m venv venv
```

## 4. Activate the virtual environment

### Windows

```powershell
venv\Scriptsctivate
```

## 5. Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Configure environment variables

Create a `.env` file locally:

```text
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=
INTERNAL_API_KEY=
DATABASE_URL=postgresql://...
```

For local-only development, SQLite may be used if supported by the current application configuration:

```text
DATABASE_URL=sqlite:///data/emi.db
```

**Never commit real credentials, API keys, database passwords, or Twilio tokens to GitHub.**

## 7. Run the application

```bash
uvicorn app:app --reload
```

---

# 🗄️ Database

The project was migrated from SQLite to **PostgreSQL for production**.

The migration utility is:

```bash
python migrate_sqlite_to_postgres.py
```

The migration covers:

- Loans
- EMIs
- Payments

The production database also contains reminder tracking used for idempotent monthly reminders.

---

# 🔔 Monthly Reminder System

The production reminder system uses a dedicated **Railway Cron** service.

The cron invokes:

```text
POST /internal/send-reminders
```

The internal endpoint is protected with:

```text
x-api-key: <INTERNAL_API_KEY>
```

The reminder service:

1. Checks whether today is the configured reminder day.
2. Finds loans with pending EMIs.
3. Identifies the next pending EMI.
4. Calculates outstanding amount and pending EMI count.
5. Sends the reminder to the borrower.
6. Sends the reminder to the lender.
7. Records the reminder for the loan and date.
8. Skips the reminder if it was already successfully sent that day.

## Idempotency

Reminder uniqueness is based on:

```text
loan_id + reminder_date
```

Therefore:

```text
First execution
    ↓
Reminder sent
    ↓
Reminder marked as sent

Second execution on same date
    ↓
Existing reminder found
    ↓
Reminder skipped
```

This protects against duplicate WhatsApp notifications caused by repeated cron executions or manual retries.

---

# ⏰ Railway Cron

The production cron is configured to run on the **10th of every month**.

Current schedule:

```text
0 9 10 * *
```

This means:

```text
09:00 UTC
14:30 IST
on the 10th of every month
```

The cron service calls the production reminder endpoint and logs the HTTP response and reminder result.

---

# 🔐 Security

- Internal reminder endpoint protected using an API key
- Twilio credentials stored as environment variables
- Database credentials stored as environment variables
- Sensitive files excluded using `.gitignore`
- Production API key should be rotated if it has ever been exposed
- Never commit `.env` or production credentials to source control

---

# 🧪 Production Verification

Before production changes, verify the following.

## API

```text
GET /
```

should return HTTP `200`.

## WhatsApp STATUS

Send:

```text
STATUS
```

Expected information includes:

- Total EMI count
- Paid EMI count
- Pending EMI count
- Outstanding amount
- Next due EMI

## Payment

Use:

```text
PAY <amount>
```

only when the corresponding payment has actually been made.

## Reminder

For controlled testing, the internal endpoint supports:

```text
POST /internal/send-reminders?force=true
```

with the correct `x-api-key`.

A successful first execution sends the reminder. Repeating the same request on the same date should skip the already-sent reminder.

---

# 🚀 Production Status

The application is deployed on **Railway** with:

- FastAPI application service
- PostgreSQL database
- Twilio WhatsApp integration
- Dedicated monthly reminder cron service
- Idempotent reminder processing

The production loan used during launch validation currently has:

```text
Total EMIs     : 14
Paid EMIs      : 1
Pending EMIs   : 13
Monthly EMI    : ₹3,000
Outstanding    : ₹39,000
```

The first EMI was paid in **August 2026** and recorded as a historical payment dated:

```text
2026-08-10
```

The next EMI is scheduled for:

```text
2026-09-10
```

The production flow has been validated for:

- Loan creation
- EMI schedule generation
- Payment recording
- WhatsApp status lookup
- Borrower notifications
- Lender notifications
- Monthly reminder execution
- Reminder idempotency
- SQLite → PostgreSQL migration
- Railway deployment

---

# 🌱 Future Enhancements

- Loan closure notification
- Enhanced payment history
- Admin dashboard
- Payment reconciliation
- OCR-based payment verification
- UPI integration
- PDF statement generation
- Production monitoring and alerting
- Automated database backup/retention strategy

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Subhojit Bhattacharjee**

Automation QA Engineer | Python | FastAPI | Playwright | Selenium | API Testing
