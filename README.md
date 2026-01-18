<img width="209" height="79" alt="Screenshot (953)" src="https://github.com/user-attachments/assets/b9fa0c05-5b2d-49e7-af70-8f36f7f7ac55" />


A web app that lets users send messages to their future selves — delivered at the perfect time.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black)
![Status](https://img.shields.io/badge/Status-Active-success)

## 🚀 Live Demo
🔗 [https://time-capsule.onrender.com](https://time-capsule-n6ck.onrender.com/)


## ✨ Features
- 📩 Create time capsules with scheduled delivery
- ⏰ Automatic email delivery at the chosen date
- 🔐 Email validation and logging
- 🗂 SQLite-based job scheduling
- 🌐 Clean and minimal UI


## 🛠 Tech Stack
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS
- **Database:** SQLite
- **Scheduler:** APScheduler
- **Deployment:** Render


## ⚙️ How It Works
1. User writes a message and selects a future delivery date
2. The app validates the email and stores the capsule
3. APScheduler tracks scheduled jobs
4. On the delivery date, the message is emailed automatically


## 🧑‍💻 Installation & Run Locally


git clone https://github.com/jshwadmaX/time-capsule.git
cd time-capsule
pip install -r requirements.txt
python app.py
Open in browser:
http://127.0.0.1:5000


## 🚧 Future Improvements
- User authentication
- Encrypted message storage
- Public capsule sharing
- Reminder notifications
- UI/UX enhancements

⭐ If you like this project, consider giving it a star!


