FROM python:3.9-slim-buster

WORKDIR /app

COPY . .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt


CMD [ "uvicorn", "main:app","--host", "0.0.0.0", "--port", "8000" ,"--reload" ]