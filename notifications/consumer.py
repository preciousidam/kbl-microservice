import pika, json, os
from datetime import datetime

from backend.models.notification import Notification
from backend.util.instances import db
from backend import create_app


app = create_app("development")

params = pika.URLParameters(os.environ.get('CELERY_BROKER_URL'))

connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.queue_declare(queue='notification')


def callback(ch, method, properties, body):
    print('Received in app')
    data = json.loads(body)

    if properties.content_type == 'item_added':

        with app.app_context():
            for item in data['dates']:
                note = Notification(leave_id=data['id'], when=item['date'])
                db.session.add(note)
                db.session.commit()



    if properties.content_type == 'item_deleted':
        with app.app_context():
            note = Notification.__table__.delete().where(Notification.leave_id == data)
            db.session.execute(note)
            db.session.commit()

    if properties.content_type == 'item_updated':
        with app.app_context():
            note = Notification.__table__.delete().where(Notification.leave_id == data['id'])
            db.session.execute(note)
            db.session.commit()
            for item in data['dates']:
                note = Notification(leave_id=data['id'], when=item['date'])
                db.session.add(note)
                db.session.commit()




channel.basic_consume(queue='notification', on_message_callback=callback, auto_ack=True)

print('Started Consuming')

channel.start_consuming()

channel.close()