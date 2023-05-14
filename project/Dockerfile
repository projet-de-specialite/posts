# pull official base image
FROM python:3.10.8-slim-buster

# set working directory
RUN mkdir -p /usr/src/posts/project
WORKDIR /usr/src/posts

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt ./project
RUN pip install -r project/requirements.txt

# add app in project directory
COPY . ./project

# run _init_database.add_tables_to_picshare_database to create the database tables
# RUN cd /usr/src/
#CMD [ "python3", "./project/src/config/db/_init_database.add_tables_to_picshare_database"]
CMD [ "python3", "./src/config/db/_init_database.py"]