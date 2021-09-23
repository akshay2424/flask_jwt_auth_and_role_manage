from app import db
from passlib.hash import pbkdf2_sha256 as sha256


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)



class TheaterModel(db.Model):
    __tablename__ = 'theaters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    no_of_seats = db.Column(db.Integer)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'id': x.id,
                'name': x.name,
                'no_of_seats': x.no_of_seats,
                'address': x.address
            }
        return {'theaters': list(map(lambda x: to_json(x), TheaterModel.query.all()))}

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()


class SeatsModel(db.Model):
    __tablename__ = 'seats'

    id = db.Column(db.Integer, primary_key=True)
    row = db.Column(db.Integer)
    number = db.Column(db.Integer)
    theater_id = db.Column(db.Integer, db.ForeignKey('theaters.id'))

    # relationship
    theater = db.relationship(
        "TheaterModel", backref=db.backref("theaters", uselist=False))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'id': x.id,
                'row': x.row,
                'number': x.number,
                'theater': x.theater.name
            }
        return {'seats': list(map(lambda x: to_json(x), SeatsModel.query.all()))}

    @classmethod
    def find_by_name(cls, row, number, theater_id):
        return cls.query.filter_by(row=row, number=number, theater_id=theater_id).first()


class ReservedSeatsModel(db.Model):
    __tablename__ = 'reserved_seats'

    id = db.Column(db.Integer, primary_key=True)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # relationship
    seat = db.relationship(
        "SeatsModel", backref=db.backref("seats", uselist=False))
    customer = db.relationship(
        "UserModel", backref=db.backref("users", uselist=False))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'seat_number': x.seat.number,
                'username': x.customer.username,
                'theater': x.seat.theater.name
            }
        return {'reserve_seats': list(map(lambda x: to_json(x), ReservedSeatsModel.query.all()))}

    @classmethod
    def find_by_name(cls, seat_id, customer_id):
        return cls.query.filter_by(seat_id=seat_id, customer_id=customer_id).first()
