import os
from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_cors import CORS
from flask_admin import Admin
from json import loads

from .models.notification import Notification
from .view import NotificationView


##############UTILITIES############
from .util.instances import initializeDB, initializeJWT, initializeMail, db
    

#create_app(test_config=None):
def create_app(env):
    # create and configure the app
    
    app = Flask(__name__, instance_relative_config=True)
   
    if env == 'development':
        # load the instance dev config, if it exists, when not testing
        app.config.from_object('instance.config.DevelopementConfig')

    elif env == 'production':
        # load the instance production config, if it exists, when not testing
        app.config.from_object('instance.config.ProductionConfig')
        
    elif env == 'testing':
        # load the test config if passed in
        app.config.from_object('instance.config.TestConfig')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

   

    #initialize Database
    initializeDB(app)

    #initialize Mail
    initializeMail(app)

    #initialize JWT 
    initializeJWT(app)

   
    '''change jsonify default JSON encoder to a custom Encode
    ### to support Model encoding for {user, properties, etc}
    '''
    #app.json_encoder = CustomJSONEncoder
    

    #Register Blueprints


    @app.after_request
    def add_header(r):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r
    

    notification_view = NotificationView.as_view('notification_api')

    app.add_url_rule('/notification/', defaults={'note_id': None}, view_func=notification_view, methods=['GET',])
    app.add_url_rule('/notification/', view_func=notification_view, methods=['POST',])
    app.add_url_rule('/notification/<int:note_id>/', view_func=notification_view, methods=['GET', 'PUT', 'DELETE'])

    
    #initialize CORS
    CORS(app)
    return app