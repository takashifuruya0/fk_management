FROM python:3.9
ENV PYTHONUNBUFFERED 1

WORKDIR /home/fk_management
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt