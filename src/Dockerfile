# Используем базовый образ Python
FROM python:3.9.10

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Скопировать файл зависимостей в текущую директорию
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt --no-cache-dir

# Копируем код приложения в контейнер
COPY . .

# Команда для запуска приложения при старте контейнера
CMD ["python", "manage.py", "runserver", "0:8000"]