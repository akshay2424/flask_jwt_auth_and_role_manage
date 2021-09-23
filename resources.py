from flask_restful import Resource, reqparse
from models import ReservedSeatsModel, SeatsModel, UserModel, TheaterModel
from flask import jsonify,abort
from functools import wraps

from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity)


def admin_require(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        print(current_user)
        user_info = UserModel.query.filter_by(username=current_user).first()
        print(user_info)
        if user_info.is_admin == True:
            return func(*args, **kwargs)
        return abort(403)
    return wrapper


class AllUsers(Resource):
    decorators = [admin_require, jwt_required()]

    def get(self):
        return UserModel.return_all()

    def delete(self):
        return UserModel.delete_all()


class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'username', help='This field cannot be blank', required=True)
        parser.add_argument(
            'password', help='This field cannot be blank', required=True)

        data = parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}

        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password'])
        )

        # try:

        new_user.save_to_db()
        access_token = create_access_token(identity=data['username'])
        refresh_token = create_refresh_token(identity=data['username'])
        return {
            'message': 'User {} was created'.format(data['username']),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        # except:
        #     return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            'username', help='This field cannot be blank', required=True)
        parser.add_argument(
            'password', help='This field cannot be blank', required=True)
        data = parser.parse_args()

        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class TheaterAPI(Resource):
    @jwt_required()
    def get(self):
        return TheaterModel.return_all()
    
    @jwt_required()
    @admin_require
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument(
            't_name', help='This field cannot be blank')
        parser.add_argument(
            'address', help='This field cannot be blank', required=True)
        parser.add_argument(
            'no_of_seats', help='This field cannot be blank', required=True)

        data = parser.parse_args()
        print(data)
        check_exist = TheaterModel.find_by_name(data['t_name'])
        if check_exist:
            return {'message': 'Theater {} already exists'.format(data['t_name'])}

        theater = TheaterModel(
            name=data['t_name'], address=data['address'], no_of_seats=data['no_of_seats'])
        theater.save_to_db()

        return {
            'message': 'Theater {} was created'.format(data['t_name']),
        }


class SeatsAPI(Resource):
    @jwt_required()
    def get(self):
        return SeatsModel.return_all()

    @jwt_required()
    @admin_require
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument(
            'row', help='This field cannot be blank')
        parser.add_argument(
            'number', help='This field cannot be blank', required=True)
        parser.add_argument(
            'theater_id', help='This field cannot be blank', required=True)

        data = parser.parse_args()
        print(data)
        check_exist = SeatsModel.find_by_name(
            data['row'], data['number'], data['theater_id'])
        if check_exist:
            return {'message': ' In Theater {} seat number {} already exists  for the row {}'.format(check_exist.theater.name, data['number'], data['row'])}

        new_seat = SeatsModel(
            row=data['row'], number=data['number'], theater_id=data['theater_id'])
        new_seat.save_to_db()

        return {
            'message': 'Seat {} was created'.format(data['number']),
        }


class ReservedSeat(Resource):
    @jwt_required()
    def get(self):
        return ReservedSeatsModel.return_all()

    @jwt_required()
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument(
            'seat_id', help='This field cannot be blank')
        parser.add_argument(
            'customer_id', help='This field cannot be blank', required=True)

        data = parser.parse_args()

        # check seats are available or not
        seat_deatils = SeatsModel.query.filter_by(id=data['seat_id']).first()
        if seat_deatils:
            get_seat_count = TheaterModel.query.filter_by(
                id=seat_deatils.theater.id).first()
        if not seat_deatils or get_seat_count.no_of_seats < 0:
            return {'message': ' In Theater {} seat number {} is not available'.format(get_seat_count.name, seat_deatils.number)}

        check_exist = ReservedSeatsModel.find_by_name(
            data['seat_id'], data['customer_id'])

        if check_exist:
            return {'message': ' In Theater {} seat number {} already reserved  for the row {}'.format(check_exist.seat.theater.name, check_exist.seat.number, check_exist.seat.row)}

        reserve_seat = ReservedSeatsModel(
            seat_id=data['seat_id'], customer_id=data['customer_id'])
        reserve_seat.save_to_db()

        # decrease 1 seat from theater
        get_seat_count.no_of_seats -= 1
        get_seat_count.save_to_db()

        return {'message': ' In Theater {} seat number {} for the row {} reserved succesfully'.format(reserve_seat.seat.theater.name, reserve_seat.seat.number, reserve_seat.seat.row)}
