from operator import le
from flask import jsonify, request
from flask.views import View, MethodView
from flask_sqlalchemy import orm
from dataclasses import asdict
from .models.notification import Notification
from .util.instances import db
from .models.notification import Notification


class NotificationView(MethodView):
    def get(self, note_id):
        if note_id is None:
            note= Notification.query.all()
            return jsonify(note), 200
        else:
            try:
                note= Notification.query.get(note_id)
                if not note:
                    return jsonify({"detail": f"data with id {note_id} does not exist"}),404
                return jsonify(note), 200
            except:
                return jsonify({"error": f"Some error occured please try again."}), 500

    
    def post(self):
        pass


    def delete(self, note_id):
        note= Notification.query.get(note_id)
        if note:
            db.session.delete(note)
            db.session.commit()
        
        return jsonify(), 204


    def put(self, note_id):
        pass