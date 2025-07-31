# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./server/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY ./server/ /app/

# Make port 57988 available to the world outside this container
# The port can be dynamically mapped by the cloud provider, but this is good practice.
EXPOSE 57988

# Command to run the application
# Use gunicorn to manage uvicorn workers for production.
# Listen on 0.0.0.0 to be accessible from outside the container.
# The port is passed via the $PORT environment variable, which Cloud Run provides.
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 0 main:socket_app 