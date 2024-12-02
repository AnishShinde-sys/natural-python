FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PORT=5000
ENV FLASK_ENV=production

EXPOSE $PORT

CMD gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 app.main:app 