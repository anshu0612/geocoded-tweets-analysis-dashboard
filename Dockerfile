FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

RUN mkdir /geocoded-tweets-analysis
WORKDIR /geocoded-tweets-analysis
COPY ./ ./

CMD ["python3", "app.py"]
