FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV FLASK_ENV=production
ENV SECRET_KEY=please-change
EXPOSE 5000
CMD ["python", "app.py"]
