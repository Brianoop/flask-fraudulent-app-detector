from flask_login import UserMixin
from . import db
from datetime import datetime
import enum


class Role(enum.Enum):
    USER = "user"
    ADMIN = "admin"

    def __str__(self):
        return self.value


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    role = db.Column(db.Enum(Role), default=Role.USER)

    mobile_application_reviews = db.relationship(
        "MobileApplicationReview", back_populates="user"
    )

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)


class MobileApplication(db.Model):
    __tablename__ = "mobile_applications"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(1000))
    logo_path = db.Column(db.String(100), unique=True)

    mobile_application_ratings = db.relationship(
        "MobileApplicationRating",
        backref=db.backref("mobile_application_ratings", uselist=False),
    )

    mobile_application_reviews = db.relationship(
        "MobileApplicationReview",
        backref=db.backref("mobile_application_reviews", uselist=False),
    )

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)


class MobileApplicationReview(db.Model):
    __tablename__ = "mobile_application_reviews"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    mobile_application_id = db.Column(
        db.Integer, db.ForeignKey("mobile_applications.id")
    )
    text = db.Column(db.String(1000))
    sentiment = db.Column(db.String(20))
    sentiment_ratio = db.Column(db.Float)

    user = db.relationship("User", back_populates="mobile_application_reviews")

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)


class MobileApplicationLike(db.Model):
    __tablename__ = "mobile_application_likes"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    mobile_application_id = db.Column(
        db.Integer, db.ForeignKey("mobile_applications.id")
    )
    user = db.relationship("User", backref=db.backref("user_app_likes", uselist=False))
    mobile_application = db.relationship(
        "MobileApplication",
        backref=db.backref("mobile_application_likes", uselist=False),
    )
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)


class MobileApplicationRating(db.Model):
    __tablename__ = "mobile_application_ratings"
    id = db.Column(
        db.Integer, primary_key=True
    )  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    mobile_application_id = db.Column(
        db.Integer, db.ForeignKey("mobile_applications.id")
    )
    rating_out_of_five = db.Column(db.Integer, default=1)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow)


db.create_all()
