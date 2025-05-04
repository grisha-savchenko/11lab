from flask import Flask, render_template, request, jsonify
import json
import os
from geopy.distance import geodesic
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Загружаем данные о клиниках
with open('clinics.json', 'r', encoding='utf-8') as f:
    clinics = json.load(f)

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