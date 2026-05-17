# Stage 1: Build React frontend
FROM node:20-alpine AS frontend
WORKDIR /app
ARG VITE_GROQ_API_KEY
ARG VITE_API_BASE_URL=/api
ENV VITE_GROQ_API_KEY=$VITE_GROQ_API_KEY
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Django backend + serve built frontend
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend /app/dist ./dist
EXPOSE 8000
CMD sh -c "python manage.py migrate --noinput && daphne -b 0.0.0.0 -p ${PORT:-8000} hireflow.asgi:application"
