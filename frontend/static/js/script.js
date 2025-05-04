document.addEventListener('DOMContentLoaded', function() {
    let map;
    let userLocation;
    let nearestClinic;
    
    // Инициализация карты
    ymaps.ready(initMap);
    
    function initMap() {
        map = new ymaps.Map('map', {
            center: [55.751244, 37.618423], // Москва по умолчанию
            zoom: 10
        });
        
        // Добавляем элементы управления
        map.controls.remove('geolocationControl');
        map.controls.remove('searchControl');
        map.controls.remove('trafficControl');
        map.controls.remove('typeSelector');
        map.controls.remove('fullscreenControl');
        map.controls.remove('rulerControl');
    }
    
    // Найти ближайшую клинику
    document.getElementById('findClinicBtn').addEventListener('click', function() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    userLocation = [position.coords.latitude, position.coords.longitude];
                    
                    // Центрируем карту на пользователе
                    map.setCenter(userLocation, 15);
                    
                    // Добавляем метку пользователя
                    const userPlacemark = new ymaps.Placemark(userLocation, {
                        hintContent: 'Ваше местоположение',
                        balloonContent: 'Вы здесь'
                    }, {
                        preset: 'islands#blueCircleIcon'
                    });
                    map.geoObjects.add(userPlacemark);
                    
                    // Запрашиваем ближайшую клинику
                    fetch('/api/nearest-clinic', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            nearestClinic = data.clinic;
                            showClinicOnMap(nearestClinic);
                        } else {
                            alert('Ошибка: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Произошла ошибка при поиске клиники');
                    });
                },
                function(error) {
                    alert('Не удалось получить ваше местоположение: ' + error.message);
                }
            );
        } else {
            alert('Геолокация не поддерживается вашим браузером');
        }
    });
    
    // Показать клинику на карте
    function showClinicOnMap(clinic) {
        // Удаляем предыдущие метки клиник
        map.geoObjects.each(function(obj) {
            if (obj.properties.get('type') === 'clinic') {
                map.geoObjects.remove(obj);
            }
        });
        
        const clinicCoords = [clinic.lat, clinic.lon];
        const clinicPlacemark = new ymaps.Placemark(clinicCoords, {
            hintContent: clinic.name,
            balloonContent: `
                <strong>${clinic.name}</strong><br>
                <address>${clinic.address}</address>
                <p>Телефон: ${clinic.phone}</p>
                <p>Режим работы: ${clinic.working_hours}</p>
            `,
            type: 'clinic'
        }, {
            preset: 'islands#redIcon'
        });
        
        map.geoObjects.add(clinicPlacemark);
        
        // Добавляем линию маршрута
        const route = new ymaps.Polyline([userLocation, clinicCoords], {}, {
            strokeColor: "#0000FF",
            strokeWidth: 4,
            strokeOpacity: 0.5
        });
        map.geoObjects.add(route);
    }
    
    // Экстренный вызов
    document.getElementById('emergencyBtn').addEventListener('click', function() {
        const phoneNumber = document.getElementById('phoneNumber').value;
        
        if (!phoneNumber) {
            alert('Пожалуйста, введите номер телефона');
            return;
        }
        
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    fetch('/api/emergency-call', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            phone: phoneNumber,
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('Ветеринар вызван! С вами свяжутся в ближайшее время.');
                        } else {
                            alert('Ошибка: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Произошла ошибка при вызове ветеринара');
                    });
                },
                function(error) {
                    alert('Не удалось получить ваше местоположение: ' + error.message);
                }
            );
        } else {
            alert('Геолокация не поддерживается вашим браузером');
        }
    });
});