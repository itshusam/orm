from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/gym_db'
db = SQLAlchemy(app)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    email = db.Column(db.String(120), unique=True, nullable=False)


class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    duration = db.Column(db.Integer)
    member_id = db.relationship('Member', backref=db.backref('workout_sessions'))


@app.route('/members', methods=['POST'])
def add_member():
    data = request.json
    new_member = Member(name=data['name'], age=data['age'], email=data['email'])
    try:
        db.session.add(new_member)
        db.session.commit()
        return jsonify({'message': 'Member added successfully'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({'error': 'Member not found'}), 400
    return jsonify({'id': member.id, 'name': member.name, 'age': member.age, 'email': member.email})

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({'error': 'Member not found'}), 400

    data = request.json
    member.name = data.get('name', member.name)
    member.age = data.get('age', member.age)
    member.email = data.get('email', member.email)

    try:
        db.session.commit()
        return jsonify({'message': 'Member updated successfully'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({'error': 'Member not found'}), 400

    try:
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Member deleted successfully'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

@app.route('/workout-sessions', methods=['POST'])
def add_workout_session():
    data = request.json
    member_id = data.get('member_id')
    member = Member.query.get(member_id)
    if not member:
        return jsonify({'error': 'Member not found'}), 400

    new_session = WorkoutSession(date=data['date'], duration=data['duration'], member_id=member_id)
    try:
        db.session.add(new_session)
        db.session.commit()
        return jsonify({'message': 'Workout session added successfully'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

@app.route('/members/<int:id>/workout-sessions', methods=['GET'])
def get_workout_sessions(id):
    member = Member.query.get(id)
    if not member:
        return jsonify({'error': 'Member not found'}), 400

    sessions = [{'id': session.id, 'date': session.date, 'duration': session.duration} for session in member.workout_sessions]
    return jsonify({'member_id': id, 'workout_sessions': sessions})


def update_workout_session(id):
    session = WorkoutSession.query.get(id)
    if not session:
        return jsonify({'error': 'Workout session not found'}), 400

    data = request.json
    session.date = data.get('date', session.date)
    session.duration = data.get('duration', session.duration)

    try:
        db.session.commit()
        return jsonify({'message': 'Workout session updated successfully'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/workout-sessions/<int:id>', methods=['DELETE'])
def delete_workout_session(id):
    session = WorkoutSession.query.get(id)
    if not session:
        return jsonify({'error': 'Workout session not found'}), 400

    try:
        db.session.delete(session)
        db.session.commit()
        return jsonify({'message': 'Workout session deleted successfully'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

with app.app_context():
      db.create_all()

if __name__ == '__main__':
  
    app.run(debug=True)