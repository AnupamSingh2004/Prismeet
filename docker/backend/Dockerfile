FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend source
COPY backend /app

# Ensure media/static dirs exist
RUN mkdir -p /media /static

CMD ["bash"]
