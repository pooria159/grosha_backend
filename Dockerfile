FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY Backend/store-backend/requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

COPY Backend/store-backend/entrypoint.sh /app/

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
