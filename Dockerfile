FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .
COPY static/ static/
COPY templates/ templates/
COPY gunicorn.conf.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]