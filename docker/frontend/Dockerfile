FROM node:18-bullseye-slim

RUN apt-get update && apt-get install -y \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ../frontend/package*.json /app/
RUN npm ci

COPY ../frontend /app

# Set environment variables for better Turbopack compatibility
ENV NEXT_TELEMETRY_DISABLED=1
ENV TURBOPACK=1

CMD ["npm", "run", "dev"]
