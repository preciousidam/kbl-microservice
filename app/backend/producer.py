import pika, json, os
from.util.jsonEncoder import CustomJSONEncoder



params = pika.URLParameters(os.environ.get('CELERY_BROKER_URL'))

connection = pika.BlockingConnection(params)

channel = connection.channel()


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='notification', body=json.dumps(body, cls=CustomJSONEncoder), properties=properties)