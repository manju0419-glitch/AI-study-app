from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
CORS(app)

# Secret key for JWT
app.config['SECRET_KEY'] = 'mysecretkey'

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(200))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')
                        )
@app.route('/')
def home():
    return "Backend running 🚀"

# Signup route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    
    email = data.get('email')
    password = generate_password_hash(data.get('password'))

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User saved"
    })

# Login route with JWT
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        if check_password_hash(user.password, password):

            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                "message": "Login successful",
                "token": token
            })
        else:
            return jsonify({
                "message": "Wrong password"
            }), 401
    else:
        return jsonify({
            "message": "User not found"
        }), 404
    # Profile route
@app.route('/profile', methods=['GET'])
def profile():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token missing"}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(data['user_id'])

        return jsonify({
            "message": "Welcome",
            "email": user.email
        })

    except:
        return jsonify({"message": "Invalid or expired token"}), 401
    
@app.route('/add-note', methods=['POST'])
def add_note():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token missing"}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']

        content = request.json.get('content')

        new_note = Note(content=content, user_id=user_id)
        db.session.add(new_note)
        db.session.commit()

        return jsonify({"message": "Note added"})

    except:
        return jsonify({"message": "Invalid token"}), 401
    
@app.route('/get-notes', methods=['GET'])
def get_notes():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token missing"}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']

        notes = Note.query.filter_by(user_id=user_id).all()

        output = []
        for note in notes:
            output.append({
                "id": note.id,
                "content": note.content
            })

        return jsonify(output)

    except:
        return jsonify({"message": "Invalid token"}), 401
    
@app.route('/delete-note/<int:id>', methods=['DELETE'])
def delete_note(id):
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token missing"}), 401

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']

        note = Note.query.filter_by(id=id, user_id=user_id).first()

        if not note:
            return jsonify({"message": "Note not found"}), 404

        db.session.delete(note)
        db.session.commit()

        return jsonify({"message": "Note deleted"})

    except:
        return jsonify({"message": "Invalid token"}), 401
    
@app.route('/summarize', methods=['POST'])
def summarize():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token missing"}), 401

    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])

        content = request.json.get('content')

        # Simple AI logic (dummy)
        words = content.split()
        summary = " ".join(words[:10])  # first 10 words

        return jsonify({
            "summary": summary + "..."
        })

    except:
        return jsonify({"message": "Invalid token"}), 401


if __name__ == '__main__':
    ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0",port=5000)