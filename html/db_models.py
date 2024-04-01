from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# initilize the collumns of table uploads in database
class Uploads(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    file_password = db.Column(db.String(100), nullable=False)
