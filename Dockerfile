# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./server/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire server directory into the container at /app
COPY ./server/ /app/

# Make port available to the world outside this container
EXPOSE 8080

# Define environment variable to tell gunicorn where to serve
ENV PORT 8080

# Run main.py when the container launches
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 0 main:socket_app 