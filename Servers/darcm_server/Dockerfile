FROM python:3
MAINTAINER Jeremy Gibson <jeremy.gibson@ncdcr.gov>

WORKDIR /usr/src/app
COPY . .
WORKDIR /usr/src/app/docker_dmc
RUN pip install --no-cache-dir -r requirements.txt
RUN python setup.py install
RUN mkdir -p /home/tomes/data
WORKDIR /usr/src/app

CMD ["python", "DarcMailServer.py"]