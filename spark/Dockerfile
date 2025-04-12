FROM bitnami/spark:3.4.1

USER root
RUN apt-get update && apt-get install -y python3-pip

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

COPY . /opt/bitnami/spark
WORKDIR /opt/bitnami/spark
