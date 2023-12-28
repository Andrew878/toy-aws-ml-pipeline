# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY ./dash_app.py /usr/src/app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /usr/src/app/
RUN pip install wheel
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x dash_app.py

# Make port 8050 available to the world outside this container
EXPOSE 8050

# Define environment variable
ENV NAME World

# Run dash_app.py when the container launches
CMD ["python", "./dash_app.py"]
