FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && \
    apt install -y libmariadb-dev && \
    apt install -y build-essential

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
COPY ./default_recipes /app/default_recipes

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]