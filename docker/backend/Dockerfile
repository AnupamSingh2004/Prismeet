FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  ffmpeg \
  python3-magic \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ../../backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY ../../backend /app

# Make media/static dirs
RUN mkdir -p /media /static

CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
