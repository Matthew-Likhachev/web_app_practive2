# Используем официальный образ Python 3.9
FROM python:3.9-slim

# Отключаем создание .pyc и буферизацию stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория в контейнере
WORKDIR /app

# Устанавливаем системные зависимости (при необходимости)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт Flask
ENV PORT=5250
EXPOSE ${PORT}

# Запуск приложения
CMD ["python", "app.py"]

