# Use a Node 18 image
FROM node:18-alpine

WORKDIR /app

# Copy package files & install dependencies
COPY ../frontend/package*.json /app/
RUN npm ci

# Copy the rest of the Next.js source
COPY ../frontend /app

# Default command (dev) – overridden in Compose
CMD ["bash", "-lc", "npm run dev"]
