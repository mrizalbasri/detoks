FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code (including engine, lexicon, and dataset folders)
COPY . .

# Expose port (documentative)
EXPOSE 8000

# Run uvicorn server with dynamic port fallback to 8000 for cloud compatibility
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
