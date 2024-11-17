FROM python:3.9-slim

WORKDIR /code

# Copy requirements first to leverage Docker cache
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory
COPY ./app /code/app/

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]