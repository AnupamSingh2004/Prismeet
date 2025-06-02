FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p /media && mkdir -p /static

# 8. Default command: run migrations, then Gunicorn
#    (Gunicorn is a production server; in dev we’ll override to runserver)
CMD ["bash", "-lc", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
