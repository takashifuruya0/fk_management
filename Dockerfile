FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN apt update && apt upgrade -y && apt clean
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./ /home/fk_management
WORKDIR /home/fk_management
RUN python3 manage.py collectstatic --no-input --settings=fk_management.environment.develop