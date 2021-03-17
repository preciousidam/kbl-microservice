import os
from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_cors import CORS
from flask_admin import Admin
from werkzeug.utils import secure_filename
from dataclasses import asdict
from pathlib import Path  # python3 only


from .view import RosterView
from .models.leave import Leave, Date
from .producer import publish


##############UTILITIES############
from .util.instances import initializeDB, initializeJWT, initializeMail, db

ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = Path('.')
    

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
    
    roster_view = RosterView.as_view('roster_api')

    app.add_url_rule('/roster/', defaults={'roster_id': None}, view_func=roster_view, methods=['GET',])
    app.add_url_rule('/roster/', view_func=roster_view, methods=['POST',])
    app.add_url_rule('/roster/<int:roster_id>/', view_func=roster_view, methods=['GET', 'PUT', 'DELETE'])

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/mass/upload/', methods=['POST'])
    def mass_upload():
        if 'file' not in request.files:
            return jsonify(dict(detail="No file part")), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify(dict(detail="No file was uploaded")), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        try:
            import csv
            filename = secure_filename(file.filename)
            with open(os.path.join(UPLOAD_FOLDER, filename), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    roster = Leave(email=row['email'], name=row['name'], ro=row['ro'], roe=row['roe'])
                    db.session.add(roster)
                    db.session.commit()
                    db.session.refresh(roster)

                    if row['date1'] != "":
                        date = Date(date=row["date1"], leave_id=roster.id)
                        db.session.add(date)

                    if row['date2'] != "":
                        date = Date(date=row["date2"], leave_id=roster.id)
                        db.session.add(date)

                    if row['date3'] != "":
                        date = Date(date=row["date3"], leave_id=roster.id)
                        db.session.add(date)

                    db.session.commit()
                    db.session.refresh(roster)
                    publish('item_added', asdict(roster))

            return jsonify(detail="Mass Upload successful"), 201
        except Exception as e:
            print(e)
            return jsonify(detail="Mass Upload failed"), 500
        


    #initialize CORS
    CORS(app)
    return app