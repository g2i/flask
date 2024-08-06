from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from xero_auth import XeroAuth
from xero_data_sync import XeroDataSync
import os

app = Flask(__name__)
xero_auth = XeroAuth()
xero_data_sync = XeroDataSync()

def scheduled_task():
    xero_auth.refresh_token()
    xero_data_sync.sync_data()


scheduler = BackgroundScheduler(timezone="UTC")
scheduler.add_job(func=scheduled_task, trigger="cron", hour=0, minute=0)
scheduler.start()

@app.route('/')
def index():
    return jsonify({"message": "Server is running 🚅"})


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
