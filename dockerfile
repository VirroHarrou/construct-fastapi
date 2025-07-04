FROM python:alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Опционально: если нужно использовать .env файл при сборке
# ARG ENV_FILE=.env
# COPY ${ENV_FILE} .env

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"] 
