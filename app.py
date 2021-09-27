from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)
api = Api(app)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo1.db'
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)
jwt = JWTManager(app)


def create_app(test_config=None):
    
    
    
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

@app.route("/")
def hello_world():
    return {"hey":"hello"}

import  models, resources
import datetime


api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.TheaterAPI, '/theaters')
api.add_resource(resources.SeatsAPI, '/seats')
api.add_resource(resources.ReservedSeat, '/reserved_seats')

from models import UserModel
@app.before_first_request
def create_tables():
    db.create_all()
    if not UserModel.query.filter_by(username = 'super').first():
        user = UserModel(
            username='super',
            password=UserModel.generate_hash('admin'),
            is_admin=True
        )
        user.save_to_db()

if __name__ == '__main__':
   app.run(debug = True)
   create_app()