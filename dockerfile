FROM python:alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Опционально: если нужно использовать .env файл при сборке
# ARG ENV_FILE=.env
# COPY ${ENV_FILE} .env

CMD [ "sh", "-c", "RUN mkdir -p /app/alembic/versions; alembic revision --autogenerate -m migration; alembic upgrade head; uvicorn app.main:app --host 0.0.0.0 --port 8000"]
