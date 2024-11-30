FROM python:3.9-slim

# Установка системных зависимостей для pandas
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Создаем директорию для данных и устанавливаем права
RUN mkdir /data && chmod 777 /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"] 