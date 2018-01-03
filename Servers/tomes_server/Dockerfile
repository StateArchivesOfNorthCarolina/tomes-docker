FROM python:3
MAINTAINER Jeremy Gibson <jeremy.gibson@ncdcr.gov>

WORKDIR /usr/src/app
COPY . .
RUN apt-get update && apt-get install -y lynx
WORKDIR /usr/src/app/tomes_tool
RUN pip install --no-cache-dir -r requirements.txt
RUN python setup.py install
RUN mkdir -p /home/tomes/data
WORKDIR /usr/src/app
CMD ["python", "TomesToolServer.py"]