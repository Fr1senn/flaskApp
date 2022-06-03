from flask_login import UserMixin, login_manager
from datetime import datetime
from sqlalchemy import CheckConstraint

from . import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    registration_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    review = db.relationship('Review', backref='user', cascade='all, delete')
    user_schedule = db.relationship('UserSchedule', backref='user')
    user_post = db.relationship('UserPost', backref='user')
    user_progress = db.relationship('UserProgress', backref='user', cascade='all, delete')
    user_subscription_duration = db.relationship('UserSubscriptionDuration', backref='user')
    user_training_schedule_attendance = db.relationship('UserTrainingScheduleAttendance', backref='user')

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


class Unit(db.Model):
    __tablename__ = 'unit'

    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(50), nullable=False)

    user_progress = db.relationship('UserProgress', backref='unit')

    def __repr__(self):
        return f'{self.unit}'


class Subscription(db.Model):
    __tablename__ = 'subscription'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)

    user_subscription_duration = db.relationship('UserSubscriptionDuration', backref='subscription')

    def __repr__(self):
        return f'{self.title}'


class SubscriptionDuration(db.Model):
    __tablename__ = 'subscription_duration'

    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Interval, unique=True, nullable=False)

    user_subscription_duration = db.relationship('UserSubscriptionDuration', backref='subscription_duration')

    def __repr__(self):
        return f'{self.duration}'


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)

    user_post = db.relationship('UserPost', backref='post')

    def __repr__(self):
        return f'{self.title}'


class Schedule(db.Model):
    __tablename__ = 'schedule'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Interval, nullable=False)

    user_schedule = db.relationship('UserSchedule', backref='schedule')

    def __repr__(self):
        return f'{self.date} {self.duration}'


class AttendanceStatus(db.Model):
    __tablename__ = 'attendance_status'

    id = db.Column(db.Integer, primary_key=True)
    attendance = db.Column(db.DateTime, nullable=False)

    user_training_schedule = db.relationship('UserTrainingScheduleAttendance', backref='attendance_status')

    def __repr__(self):
        return f'{self.attendance}'


class TrainingSchedule(db.Model):
    __tablename__ = 'training_schedule'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Interval, nullable=False)

    training_schedule = db.relationship('UserTrainingScheduleAttendance', backref='training_schedule')

    def __repr__(self):
        return f'{self.date} {self.duration}'


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'{self.date} {self.user_id}'


class UserSchedule(db.Model):
    __tablename__ = 'user_schedule'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)

    def __repr__(self):
        return f'{self.user_id} {self.schedule_id}'


class UserPost(db.Model):
    __tablename__ = 'user_post'

    id = db.Column(db.Integer, primary_key=True)
    salary = db.Column(db.Numeric(7, 2), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f'{self.user_id} {self.post_id}'


class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    value = db.Column(db.Numeric(5, 2), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)

    def __repr__(self):
        return f'{self.user_id} {self.value} {self.date}'


class UserSubscriptionDuration(db.Model):
    __tablename__ = 'user_subscription_duration'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    price = db.Column(db.Numeric(5, 2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=False)
    subscription_duration_id = db.Column(db.Integer, db.ForeignKey('subscription_duration.id'), nullable=False)

    def __repr__(self):
        return f'{self.user_id} {self.value} {self.date}'


class UserTrainingScheduleAttendance(db.Model):
    __tablename__ = 'user_training_schedule_attendance'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('attendance_status.id'), nullable=False)
    training_schedule_id = db.Column(db.Integer, db.ForeignKey('training_schedule.id'))
