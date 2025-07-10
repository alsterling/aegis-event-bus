FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
# This copies the 'app' folder and its contents into /code/app
COPY ./app ./app

# The command to run when the container starts
# It now correctly points to the 'app' object inside the 'main' module
# which is inside the 'app' package.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]