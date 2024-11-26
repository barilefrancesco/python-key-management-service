FROM python:3.9-slim

WORKDIR /kms

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy requirements first to leverage Docker cache
COPY requirements.txt /kms/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the .env file
COPY .env /kms/

# Copy the app directory
COPY ./app /kms/app/

# Copy the logs directory
COPY ./logs /kms/logs/
# Make the crontab.sh script executable
RUN chmod +x /kms/logs/crontab.sh

# Create the data directory
RUN mkdir -p /kms/data


# Command to run the application and start the cron job
CMD ["/bin/sh", "-c", "/kms/logs/crontab.sh && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]