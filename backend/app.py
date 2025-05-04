from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from geopy.distance import geodesic
from dotenv import load_dotenv
from models import db, User

load_dotenv()

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY')

db.init_app(app)

# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()

# Загружаем данные о клиниках
with open('clinics.json', 'r', encoding='utf-8') as f:
    clinics = json.load(f)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name', '')
        bank_account = request.form['bank_account']
        
        if User.query.filter_by(username=username).first():
            return jsonify({'status': 'error', 'message': 'Username already exists'}), 400
            
        new_user = User(
            username=username,
            password=password,
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            bank_account=bank_account
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        return jsonify({'status': 'success', 'redirect': url_for('index')})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return jsonify({'status': 'success', 'redirect': url_for('index')})
        
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

def find_nearest_clinic(user_coords):
    nearest = None
    min_distance = float('inf')
    
    for clinic in clinics:
        clinic_coords = (clinic['lat'], clinic['lon'])
        distance = geodesic(user_coords, clinic_coords).km
        if distance < min_distance:
            min_distance = distance
            nearest = clinic
    
    return nearest

@app.route('/')
def index():
    return render_template('index.html', yandex_maps_api_key=os.getenv('YANDEX_MAPS_API_KEY'))

@app.route('/api/nearest-clinic', methods=['POST'])
def get_nearest_clinic():
    data = request.json
    try:
        user_coords = (data['latitude'], data['longitude'])
        nearest_clinic = find_nearest_clinic(user_coords)
        return jsonify({'status': 'success', 'clinic': nearest_clinic})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/emergency-call', methods=['POST'])
def emergency_call():
    data = request.json
    try:
        # Здесь должна быть логика вызова ветеринара
        # Например, отправка SMS или email с данными
        print(f"Экстренный вызов! Телефон: {data['phone']}, Координаты: {data['latitude']}, {data['longitude']}")
        return jsonify({'status': 'success', 'message': 'Ветеринар вызван'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)