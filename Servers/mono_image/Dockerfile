FROM mono:latest
MAINTAINER Jeremy Gibson <jeremy.gibson@ncdcr.gov>

WORKDIR /usr/src/app
COPY . .
ENTRYPOINT ["mono", "/usr/src/app/tomes_pst_extractor/TomesPst2Mime.exe"]