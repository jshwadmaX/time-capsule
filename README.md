<div align="center">

# ⏳ CronoVault — Next-Gen Time Capsule

**Preserve your memories and send them across time.**  
Write a message, attach files, pick a future date — CronoVault delivers it straight to your inbox when the moment arrives.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![APScheduler](https://img.shields.io/badge/APScheduler-3.x-4CAF50?style=for-the-badge)](https://apscheduler.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## ✨ Features

- 🔐 **Fernet Encryption** — capsule contents are encrypted at rest until delivery
- 📅 **Scheduled Delivery** — powered by APScheduler with SQLite persistence (survives restarts)
- 📎 **File Attachments** — attach photos, videos, documents, and more
- 📧 **Gmail SMTP** — reliable email delivery with HTML-formatted emails
- 🤖 **AI Time Assistant** — built-in chat companion on the dashboard
- 🌌 **Interactive Starfield** — particle canvas background that reacts to your cursor
- ☁️ **Render-Ready** — includes `render.yaml` for one-click cloud deployment

---

## 📸 Screenshots

| Landing Page | Dashboard |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/dc466966-be2f-4384-98bd-e3fca92fd14d" alt="Landing Page" width="100%"> | <img src="https://github.com/user-attachments/assets/939c289c-5384-4175-8773-02e25101fbf5" alt="Dashboard" width="100%"> |

| Capsule Form | Email Preview |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/8f505057-e48f-4d19-b790-80266a3f59e7" alt="Capsule Form" width="100%"> | <img src="https://github.com/user-attachments/assets/9375ad46-45d0-45ef-a3f1-d3f9f9f55150" alt="Email Preview" width="100%"> |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+, Flask |
| Job Scheduling | APScheduler + SQLAlchemy (SQLite) |
| Encryption | `cryptography` (Fernet) |
| Email | `smtplib` — Gmail SMTP / TLS |
| Frontend | Vanilla JS, HTML5 Canvas |
| Deployment | Gunicorn, Render |

---

## 🚀 Getting Started

### Prerequisites

- Python **3.9+**
- A **Gmail account** with an [App Password](https://myaccount.google.com/apppasswords) (required if 2FA is on)
- `pip` or `pip3`

---

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/next-gen-time-capsule.git
cd next-gen-time-capsule
```

---

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Copy the example file and fill in your credentials:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set your values:

| Variable | Description |
|---|---|
| `SMTP_EMAIL` | Your Gmail address (e.g. `you@gmail.com`) |
| `SMTP_PASSWORD` | Your [Gmail App Password](https://myaccount.google.com/apppasswords) (NOT your account password) |
| `ENCRYPTION_SECRET` | Any long random string — used to encrypt capsule data at rest |

> ⚠️ **Never commit `.env` to version control.** It's already in `.gitignore`.

---

### 5. Load Environment Variables

**Windows (PowerShell):**

```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^([^#][^=]+)=(.+)$') {
    [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim(), 'Process')
  }
}
```

**macOS / Linux:**

```bash
export $(grep -v '^#' .env | xargs)
```

Or install [python-dotenv](https://pypi.org/project/python-dotenv/) and it will be loaded automatically if you add `from dotenv import load_dotenv; load_dotenv()` to `app.py`.

---

### 6. Run the App

```bash
python app.py
```

The server starts at **http://localhost:5000** 🎉

---

### 7. Test Email Sending

Visit this URL to trigger a test email immediately (no scheduling):

```
http://localhost:5000/test-email
```

> Edit line 472 of `app.py` to change the test recipient address before running.

---

## 🗺️ Routes Reference

| Route | Method | Description |
|---|---|---|
| `/` | GET | Landing page |
| `/signup` | GET, POST | Sign up |
| `/login` | GET, POST | Login |
| `/dashboard` | GET, POST | Create & schedule a time capsule |
| `/capsules` | GET | List all saved capsules (JSON) |
| `/scheduled-jobs` | GET | View scheduled APScheduler jobs (JSON) |
| `/test-email` | GET | Send a test email immediately |
| `/instructions` | GET | Instructions page |
| `/logout` | GET | Logout |

---

## ☁️ Deploy to Render (Free)

The repo already includes a [`render.yaml`](render.yaml) for zero-config deployment.

1. Push your code to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service** → connect your repo.
3. Render auto-detects `render.yaml` and configures the service.
4. Add your environment variables in the Render dashboard under **Environment**:
   - `SMTP_EMAIL`
   - `SMTP_PASSWORD`
   - `ENCRYPTION_SECRET`
5. Click **Deploy** — done! 🚀

> **Note:** Render's free tier spins down after inactivity. Scheduled jobs may miss their window. Upgrade to a paid plan for reliable cron-like scheduling.

---

## 📁 Project Structure

```
next-gen-time-capsule/
├── app.py                  # Main Flask app & scheduler
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── .env.example            # Environment variable template
├── scheduled_jobs.db       # SQLite job store (auto-created)
├── capsules/               # Encrypted .enc capsule files (auto-created)
├── uploads/                # Temporary file uploads (auto-created)
├── static/
│   ├── css/
│   │   ├── styles.css
│   │   ├── globals.css
│   │   ├── login-styles.css
│   │   └── signup-styles.css
│   └── js/
│       └── script.js
└── templates/
    ├── landing.html
    ├── signup.html
    ├── login.html
    ├── dashboard.html
    ├── instructions.html
    └── profile.html
```

---

## 🔒 Security Notes

- Capsule content is **Fernet-encrypted** on disk using a key derived from `ENCRYPTION_SECRET`.
- Only metadata (recipient, dates, status) is exposed via the `/capsules` API — never the message.
- Files are deleted from the server after a successful email delivery.
- For production, store `ENCRYPTION_SECRET` in a secrets manager (e.g., Render Secret Files, AWS Secrets Manager).

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ and a touch of stardust ✨
</div>
