FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 10000

CMD ["gunicorn", "app:app"]