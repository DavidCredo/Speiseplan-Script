FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

# Set the entrypoint to run the Flask application using gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:80", "main:app"]
