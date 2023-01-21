FROM python:3.8.14-slim-bullseye

COPY . /data_train

WORKDIR /data_train

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN pip install tensorflow==2.8.0
EXPOSE 8080

CMD ["python","main.py"]