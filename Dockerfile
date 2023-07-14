# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install setuptools==45
RUN pip3 install -r requirements.txt

# specifies a port number for our image to run in a docker container
EXPOSE 5000

COPY . .

ENV FLASK_APP=__init__.py

CMD ["python", "-m" , "flask", "run", "--host", "0.0.0.0"]