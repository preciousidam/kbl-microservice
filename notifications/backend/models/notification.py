from backend.util.instances import db
from dataclasses import dataclass
from datetime import date

@dataclass
class Notification(db.Model):
    id: int
    leave_id: int
    when: str
    is_due: bool

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    leave_id = db.Column(db.Integer, nullable=False)
    when = db.Column(db.DateTime(timezone=True), nullable=False)

    @property
    def is_due(self):
        diff = self.when - date.today()
        if diff.days == 14 or diff.days== 7:
            return True
        
        return False