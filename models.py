from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.Integer, default=1)
	login_id = db.Column(db.String(32))
	email = db.Column(db.String(128))
	password = db.Column(db.String(128))
	nickname = db.Column(db.String(128))
	created_at = db.Column(db.DateTime)
	updated_at = db.Column(db.DateTime)


