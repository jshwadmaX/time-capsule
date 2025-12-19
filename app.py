from flask import Flask, render_template, redirect, url_for, request, jsonify
from werkzeug.utils import secure_filename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import os
from datetime import datetime
import logging
import json
from cryptography.fernet import Fernet
import base64
import hashlib
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# Scheduler imports with persistence
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)

# Configuration
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = "uploads"
CAPSULES_FOLDER = "capsules"  # New folder for encrypted capsules
ALLOWED_EXTENSIONS = {
    "txt",
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "doc",
    "docx",
    "zip",
    "mp4",
    "mov",
}

# Create necessary folders
for folder in [UPLOAD_FOLDER, CAPSULES_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CAPSULES_FOLDER"] = CAPSULES_FOLDER

# Email Configuration
SENDER_EMAIL = os.getenv("SMTP_EMAIL")
SENDER_PASSWORD = os.getenv("SMTP_PASSWORD")


# Encryption key (in production, store this securely, not in code!)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_SECRET", "dev-secret").encode()
# Must be 32 bytes for Fernet
# Generate a proper Fernet key from the secret
cipher_key = base64.urlsafe_b64encode(hashlib.sha256(ENCRYPTION_KEY).digest())
cipher = Fernet(cipher_key)

# Initialize scheduler with SQLite persistence
jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///scheduled_jobs.db")}
executors = {"default": ThreadPoolExecutor(max_workers=10)}
job_defaults = {
    "coalesce": False,
    "max_instances": 3,
    "misfire_grace_time": 3600,  # 1 hour grace period for missed jobs
}

scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=pytz.timezone("Asia/Kolkata")
)

scheduler.start()
logger.info("Scheduler started successfully (IST)")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def encrypt_capsule_data(capsule_data):
    """Encrypt capsule data using Fernet encryption"""
    try:
        json_data = json.dumps(capsule_data)
        encrypted_data = cipher.encrypt(json_data.encode())
        return encrypted_data
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return None


def decrypt_capsule_data(encrypted_data):
    """Decrypt capsule data"""
    try:
        decrypted_data = cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return None


def save_encrypted_capsule(
    recipient_email, message, unlock_date, unlock_time, files, job_id
):
    """Save encrypted capsule to disk"""
    try:
        capsule_data = {
            "recipient_email": recipient_email,
            "message": message,
            "unlock_date": unlock_date,
            "unlock_time": unlock_time,
            "files": files if files else [],
            "created_at": datetime.now().isoformat(),
            "job_id": job_id,
            "status": "scheduled",
        }

        # Encrypt the data
        encrypted_data = encrypt_capsule_data(capsule_data)
        if not encrypted_data:
            return None

        # Save to file
        capsule_filename = f"capsule_{job_id}.enc"
        capsule_path = os.path.join(app.config["CAPSULES_FOLDER"], capsule_filename)

        with open(capsule_path, "wb") as f:
            f.write(encrypted_data)

        logger.info(f"Encrypted capsule saved: {capsule_path}")
        return capsule_path

    except Exception as e:
        logger.error(f"Error saving encrypted capsule: {e}")
        return None


def load_encrypted_capsule(capsule_path):
    """Load and decrypt capsule from disk"""
    try:
        with open(capsule_path, "rb") as f:
            encrypted_data = f.read()

        capsule_data = decrypt_capsule_data(encrypted_data)
        return capsule_data

    except Exception as e:
        logger.error(f"Error loading encrypted capsule: {e}")
        return None


def update_capsule_status(job_id, status):
    """Update capsule status after sending"""
    try:
        capsule_filename = f"capsule_{job_id}.enc"
        capsule_path = os.path.join(app.config["CAPSULES_FOLDER"], capsule_filename)

        if os.path.exists(capsule_path):
            capsule_data = load_encrypted_capsule(capsule_path)
            if capsule_data:
                capsule_data["status"] = status
                capsule_data["sent_at"] = datetime.now().isoformat()

                encrypted_data = encrypt_capsule_data(capsule_data)
                with open(capsule_path, "wb") as f:
                    f.write(encrypted_data)

                logger.info(f"Capsule status updated to: {status}")

    except Exception as e:
        logger.error(f"Error updating capsule status: {e}")


def send_time_capsule_email(
    recipient_email, message, unlock_date, unlock_time, files=None, job_id=None
):
    """Send time capsule message via email"""
    logger.info(f"Attempting to send time capsule to {recipient_email}")

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Date"] = formatdate(localtime=True)
        msg["Subject"] = f"🎁 Time Capsule - Unlocked on {unlock_date} at {unlock_time}"

        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4CAF50;">⏰ Your Time Capsule Has Been Unlocked!</h2>
            <p><strong>Scheduled Unlock Date:</strong> {unlock_date}</p>
            <p><strong>Scheduled Unlock Time:</strong> {unlock_time}</p>
            <hr style="border: 1px solid #ddd;">
            <div style="margin-top: 20px; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #4CAF50;">
                <p style="white-space: pre-wrap;">{message}</p>
            </div>
            <hr style="border: 1px solid #ddd; margin-top: 20px;">
            <p style="color: #666; font-size: 12px;">This is an automated message from Time Capsule App</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(email_body, "html"))

        # Attach files if they exist
        attached_files = []
        if files:
            for file_path in files:
                if os.path.exists(file_path):
                    try:
                        attachment = MIMEBase("application", "octet-stream")
                        with open(file_path, "rb") as f:
                            attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)
                        attachment.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=os.path.basename(file_path),
                        )
                        msg.attach(attachment)
                        attached_files.append(file_path)
                        logger.info(f"Attached file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error attaching file {file_path}: {e}")
                else:
                    logger.warning(f"File not found: {file_path}")

        # Send email
        logger.info("Connecting to SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email sent successfully to {recipient_email}")

        # Update capsule status to "sent"
        if job_id:
            update_capsule_status(job_id, "sent")

        # Cleanup files ONLY after successful send
        if attached_files:
            for file_path in attached_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Cleaned up file: {file_path}")
                except Exception as e:
                    logger.error(f"Error cleaning up file {file_path}: {e}")

        return True, "Email sent successfully"

    except smtplib.SMTPAuthenticationError:
        error_msg = "Email authentication failed. Check sender credentials."
        logger.error(error_msg)
        if job_id:
            update_capsule_status(job_id, "failed")
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        logger.error(error_msg)
        if job_id:
            update_capsule_status(job_id, "failed")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        if job_id:
            update_capsule_status(job_id, "failed")
        return False, error_msg


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        return redirect(url_for("dashboard", email=email))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        return redirect(url_for("dashboard", email=email))
    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    email = request.args.get("email", "admin@timecapsule.com")

    if request.method == "POST":
        recipient_email = request.form.get("recipient_email", "").strip()
        message = request.form.get("message", "").strip()
        unlock_date = request.form.get("unlockDate", "").strip()
        unlock_time = request.form.get("unlockTime", "").strip()

        if not all([recipient_email, message, unlock_date, unlock_time]):
            return jsonify({"success": False, "message": "Please fill all fields"})

        # Validate email format
        if "@" not in recipient_email:
            return jsonify({"success": False, "message": "Invalid email address"})

        # Process files
        files = []
        if "files" in request.files:
            for file in request.files.getlist("files"):
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(filepath)
                    files.append(filepath)
                    logger.info(f"File saved: {filepath}")

        try:
            # Convert date & time to datetime
            send_datetime = datetime.strptime(
                f"{unlock_date} {unlock_time}", "%Y-%m-%d %H:%M"
            )

            # Check if scheduled time is in the past
            if send_datetime <= datetime.now():
                # Clean up files if time is in past
                for f in files:
                    if os.path.exists(f):
                        os.remove(f)
                return jsonify(
                    {
                        "success": False,
                        "message": "⚠️ Scheduled time must be in the future!",
                    }
                )

            # Generate unique job ID
            job_id = f"capsule_{datetime.now().timestamp()}_{recipient_email}"

            # Save encrypted capsule
            capsule_path = save_encrypted_capsule(
                recipient_email, message, unlock_date, unlock_time, files, job_id
            )

            # Schedule email
            job = scheduler.add_job(
                send_time_capsule_email,
                "date",
                run_date=send_datetime,
                args=[
                    recipient_email,
                    message,
                    unlock_date,
                    unlock_time,
                    files if files else None,
                    job_id,
                ],
                id=job_id,
                replace_existing=False,
            )

            logger.info(
                f"Time capsule scheduled for {send_datetime} (Job ID: {job.id})"
            )

            return jsonify(
                {
                    "success": True,
                    "message": f"⏳ Time Capsule scheduled successfully for {unlock_date} at {unlock_time}!",
                    "job_id": job.id,
                    "capsule_saved": capsule_path is not None,
                }
            )

        except ValueError as e:
            # Clean up files on error
            for f in files:
                if os.path.exists(f):
                    os.remove(f)
            return jsonify({"success": False, "message": "Invalid date or time format"})
        except Exception as e:
            logger.error(f"Error scheduling job: {e}")
            # Clean up files on error
            for f in files:
                if os.path.exists(f):
                    os.remove(f)
            return jsonify({"success": False, "message": f"Error: {str(e)}"})

    return render_template("dashboard.html", email=email, sender_email=SENDER_EMAIL)


@app.route("/scheduled-jobs")
def scheduled_jobs():
    """View all scheduled jobs (for debugging)"""
    jobs = scheduler.get_jobs()
    jobs_list = []
    for job in jobs:
        jobs_list.append(
            {"id": job.id, "next_run": str(job.next_run_time), "name": job.name}
        )
    return jsonify({"scheduled_jobs": jobs_list, "count": len(jobs_list)})


@app.route("/capsules")
def list_capsules():
    """List all encrypted capsules"""
    try:
        capsules = []
        capsule_files = [
            f for f in os.listdir(app.config["CAPSULES_FOLDER"]) if f.endswith(".enc")
        ]

        for capsule_file in capsule_files:
            capsule_path = os.path.join(app.config["CAPSULES_FOLDER"], capsule_file)
            capsule_data = load_encrypted_capsule(capsule_path)

            if capsule_data:
                # Don't expose the actual message, just metadata
                capsules.append(
                    {
                        "job_id": capsule_data.get("job_id"),
                        "recipient": capsule_data.get("recipient_email"),
                        "unlock_date": capsule_data.get("unlock_date"),
                        "unlock_time": capsule_data.get("unlock_time"),
                        "created_at": capsule_data.get("created_at"),
                        "status": capsule_data.get("status"),
                        "has_files": len(capsule_data.get("files", [])) > 0,
                        "file_count": len(capsule_data.get("files", [])),
                    }
                )

        return jsonify({"capsules": capsules, "count": len(capsules)})

    except Exception as e:
        logger.error(f"Error listing capsules: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/test-email")
def test_email():
    """Test email sending immediately"""
    success, message = send_time_capsule_email(
        recipient_email="your-test-email@gmail.com",  # Change this
        message="This is a test time capsule message!",
        unlock_date=datetime.now().strftime("%Y-%m-%d"),
        unlock_time=datetime.now().strftime("%H:%M"),
        files=None,
        job_id="test_capsule",
    )
    return jsonify({"success": success, "message": message})


@app.route("/instructions")
def instructions():
    return render_template("instructions.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/logout")
def logout():
    return redirect(url_for("landing"))


# Graceful shutdown
import atexit


@atexit.register
def shutdown():
    logger.info("Shutting down scheduler...")
    scheduler.shutdown()


if __name__ == "__main__":
    try:
        app.run(
            debug=True, use_reloader=False
        )  # use_reloader=False prevents double scheduler
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application shutdown requested")
        scheduler.shutdown()

