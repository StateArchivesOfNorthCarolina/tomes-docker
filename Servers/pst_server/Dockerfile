FROM python:3
MAINTAINER Jeremy Gibson <jeremy.gibson@ncdcr.gov>

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /home/tomes/data
CMD ["python", "PstConverter.py"]