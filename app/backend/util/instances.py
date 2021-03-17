from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from celery import Celery

from flask_migrate import Migrate


mail = Mail()
db = SQLAlchemy()
jwt = JWTManager()



def initializeDB(app):
    db.init_app(app)
    Migrate(app, db)


def initializeJWT(app):
    jwt.init_app(app)

def initializeMail(app):
    mail.init_app(app) 

def initializeCelery(app):
    
    print(app.config['BROKER'])

    celery = Celery(
        app.import_name,
        backend=app.config['RESULT_BACKEND'],
        broker=app.config['BROKER']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery