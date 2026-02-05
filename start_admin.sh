#!/bin/bash
echo "--- Balthomes Admin Setup & Start ---"
cd "$(dirname "$0")"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Ошибка: python3 не найден. Пожалуйста, установите Python."
    exit 1
fi

echo "Проверка зависимостей..."
python3 -m pip install flask flask-cors &> /dev/null

echo "Запуск сервера..."
# Open browser after a short delay
(sleep 2 && open "http://localhost:8000/admin") &

python3 admin_server.py
