FROM python:3.10
# Set environment variable for Kafka bootstrap servers
ENV KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Install dependencies
RUN apt-get update \
    && apt-get install -y gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
ADD requirements.txt .

# Install Django
RUN pip install -r requirements.txt

# Copy Django project into container
WORKDIR /app
COPY . /app

# Expose port 8000 for Django development server
EXPOSE 8000

# Start Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0"]
# CMD ["python", "notifications_reports_app/python expenses_notification_consumer.py"]
# CMD ["python", "notifications_reports_app/python expenses_reports_consumer.py"]
