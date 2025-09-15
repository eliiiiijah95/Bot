# 1. Базовый образ Python
FROM python:3.11-slim

# 2. Рабочая директория внутри контейнера
WORKDIR /app

# 3. Копируем только файл зависимостей сначала
# это ускоряет сборку, если код будет меняться
COPY requirements.txt .

# 4. Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем весь код проекта
COPY . .

# 6. Переменная окружения для Python
ENV PYTHONUNBUFFERED=1

# 7. Точка входа — запуск монолита
CMD ["python", "main.py"]
