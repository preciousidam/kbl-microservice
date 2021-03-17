from celery.schedules import crontab
from .util.instances import initializeCelery
from . import create_app
from flask_mail import Message

from .util.instances import mail


celery = initializeCelery(create_app('development'))
celery.conf.enable_utc = False

@celery.task
def send_reminder():
    try:
        print('sending...')
        msg = Message(
                subject='Testing', 
                body='Leave date is nextweek', 
                sender="napims.support@cortts.com", 
                recipients=['preciousidam@gmail.com', 'preciousidam@yahoo.com']
            )
        mail.send(msg)
        print('sent:(')
    except Exception as e:
        print(e)



celery.conf.beat_schedule = {
    'leave_roster_task': dict(task='backend.celery.send_reminder', schedule=crontab(hour=8, minute=0))
}