# Using slim python
FROM python:3.11-slim

# setup working directory
WORKDIR /app

# Avoid Cache
ENV PYTHONDONTWRITEBYTECODE=1
# docker Log output app enable
ENV PYTHONUNBUFFERED=1

#run update and installation if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy requirement to docker app
COPY requirements.txt /app/

# installing or upgrade library
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copy source to docker app
COPY . /app/

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9999", "--reload"]
