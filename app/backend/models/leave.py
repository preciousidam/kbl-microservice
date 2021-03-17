from backend.util.instances import db
from dataclasses import dataclass

@dataclass
class Leave(db.Model):
    id: int
    name: str
    email: str
    ro: str
    roe: str
    dates: list

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    ro = db.Column(db.String(255), nullable=False, default="")
    roe = db.Column(db.String(255), nullable=False, default="")
    dates = db.relationship('Date', back_populates='leave', cascade='all, delete, delete-orphan', passive_deletes=True)


    def __str__(self):
        return self.name


@dataclass
class Date(db.Model):
    date: str

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date(), nullable=False)
    leave_id = db.Column(db.Integer, db.ForeignKey('leave.id', ondelete='CASCADE'), nullable=False)
    leave = db.relationship("Leave", back_populates="dates")
