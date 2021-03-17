from celery.schedules import crontab
import os
from requests import get
from .util.instances import initializeCelery
from . import create_app
from flask_mail import Message

from .util.instances import mail
from .models.notification import Notification

celery = initializeCelery(create_app('development'))
celery.conf.enable_utc = False

def mail_body(name, date):
    return f'Dear {name}, \n\n\rYou have been working very hard and we think you deserve some rest. This is to remind you that that your leave is due on {date}, according to the roster.\n\n\rKindly apply for your leave or discuss with your supervisor/HR for further enquiries.\n\n\rBest regards.'

def get_user_detail(roster_id):
    res = get(f'{os.environ.get("ROSTER_URL")}/roster/{roster_id}/')
    data = res.json()
    return data

@celery.task
def get_due():
    notes = Notification.query.all()

    for index, note in enumerate(notes):
        if note.is_due:
            send_reminder(note.leave_id, note.when)

            print("Notification queued")
    
    print("task Ended")


@celery.task
def send_reminder(roster_id, when):
    data = get_user_detail(roster_id)
    try:
        print('sending...')
        msg = Message(
                subject='Reminder: Your annual leave is due', 
                body=mail_body(data['name'], when), 
                sender="no_reply@kblinsurance.com", 
                recipients=[data['email'], data['roe']]
            )
        mail.send(msg)
        print('Mail sent')
    except Exception as e:
        print(e)
        print('Mail sending failed')



celery.conf.beat_schedule = {
    'leave_roster_task': dict(task='backend.celery.get_due', schedule=crontab(minute="*"))
}