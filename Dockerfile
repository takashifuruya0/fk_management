FROM python:3.9
ENV PYTHONUNBUFFERED 1
COPY ./ /home/fk_management
WORKDIR /home/fk_management
ADD requirements.txt requirements.txt
RUN apt update && apt upgrade -y && apt clean
RUN pip3 install -r requirements.txt
RUN python3 manage.py collectstatic --no-input --settings=fk_management.environment.develop