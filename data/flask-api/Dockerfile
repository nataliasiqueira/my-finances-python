FROM python:3.11

WORKDIR /data/flask-api

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]