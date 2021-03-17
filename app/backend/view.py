from operator import le
from flask import jsonify, request
from flask.views import View, MethodView
from flask_sqlalchemy import orm
from dataclasses import asdict
from .models.leave import Leave
from .util.instances import db
from .models.leave import Leave, Date
from .producer import publish


class RosterView(MethodView):
    def get(self, roster_id):
        if roster_id is None:
            roster = Leave.query.all()
            return jsonify(roster), 200
        else:
            try:
                roster = Leave.query.get(roster_id)
                if not roster:
                    return jsonify({"detail": f"data with id {roster_id} does not exist"}),404
                return jsonify(roster), 200
            except:
                return jsonify({"error": f"Some error occured please try again."}), 500

    
    def post(self):
        data = request.get_json()

        if not data:
            return jsonify(dict(name="No data was submited")), 400

        if 'name' not in data:
            return jsonify(dict(name=" Please name cannot be blank")), 400

        if 'email' not in data:
            return jsonify(dict(email="Please email cannot be blank")), 400

        if 'roe' not in data:
            return jsonify(dict(name="Please provide relief officer email")), 400

        if 'ro' not in data:
            return jsonify(dict(email="Please provide relief officer name")), 400

        if 'dates' not in data:
            return jsonify(dict(when="Please select leave period")), 400

        
        leave = Leave(name=data.get('name'), email=data.get('email'), roe=data.get('roe'), ro=data.get('ro'))
        db.session.add(leave)
        db.session.commit()

        for date in data.get('dates'):
            date = Date(date=date['date'], leave_id=leave.id)
            db.session.add(date)
            db.session.commit()

        db.session.refresh(leave)
        publish('item_added', asdict(leave))
        return jsonify(leave), 201


    def delete(self, roster_id):
        roster = Leave.query.get(roster_id)
        if roster:
            db.session.delete(roster)
            db.session.commit()
            publish('item_deleted', roster_id)
            
        return jsonify(), 204
        


    def put(self, roster_id):
        data = request.get_json()

        leave = Leave.query.get(roster_id)

        if 'dates' in data:
            dates = Date.__table__.delete().where(Leave.id == roster_id)
            db.session.execute(dates)
            db.session.commit()
            for date in data.get('dates'):
                date = Date(date=date['date'], leave_id=leave.id)
                db.session.add(date)
                db.session.commit()

            data.pop("dates")

        if "email" in data:
            leave.email = data['email']
        if "name" in data:
            leave.name = data['name']
        if "ro" in data:
            leave.email = data['ro']
        if "roe" in data:
            leave.name = data['roe']

        db.session.commit()

        db.session.refresh(leave)
        publish('item_updated', asdict(leave))
        return jsonify(leave), 201