# start from official Python image
FROM python:3.11-slim

# set working directory inside container
WORKDIR /app

# copy requirements first (Docker caches this layer — faster rebuilds)
COPY requirements.txt .

# install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy rest of the code
COPY . .

# expose port 5000
EXPOSE 5000

# command to run the app
CMD ["python", "app.py"]