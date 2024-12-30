from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = "((*DSKLFJLSKJF)(W(#)))"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:lkjhg09876@localhost/quanlychuyenbay2?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 8
db = SQLAlchemy(app)
login = LoginManager(app)
cloudinary.config(
    cloud_name='dx6brcofe',
    api_key='716129595449135',
    api_secret='drKg8CvyTumADgnoKln06YGRfss'
)
