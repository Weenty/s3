FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONNUNBUFFERED 1

WORKDIR /code

RUN apt-get update && \
    apt install -y python3
  
RUN pip install --upgrade pip

COPY . .

RUN pip install -r req.txt

EXPOSE 8000
