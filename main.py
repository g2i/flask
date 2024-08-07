from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from src.services.xero.xero_auth import XeroAuth
from src.services.xero.xero_data_sync import XeroDataSync
import os

app = Flask(__name__)

xero_auth = XeroAuth()
xero_data_sync = XeroDataSync()

def refresh_token():
    xero_auth.refresh_token()

def sync_data():
    xero_data_sync.sync_data()

def scheduled_task():
    refresh_token()
    sync_data()

scheduler = BackgroundScheduler(timezone="UTC")
scheduler.add_job(func=scheduled_task, trigger="cron", hour=0, minute=0)
scheduler.start()

@app.route('/')
def index():
    return jsonify({"message": "Server is running 🚅"})

if __name__ == '__main__':
    # Run the scheduled task once at startup
    scheduled_task()
    app.run(debug=True, port=os.getenv("PORT", default=5000))