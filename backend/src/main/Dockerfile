# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY ./main.py /usr/src/app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /usr/src/app/
RUN pip install wheel
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install Uvicorn for ASGI support
RUN pip install uvicorn

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
