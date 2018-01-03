FROM anapsix/alpine-java
MAINTAINER Jeremy Gibson <jeremy.gibson@ncdcr.gov>
RUN apk add --update --no-cache \
	 unzip \
	 wget
WORKDIR /usr/src/app

RUN wget http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip && \
    unzip stanford-corenlp-full-2017-06-09.zip && \
	rm stanford-corenlp-full-2017-06-09.zip

WORKDIR /usr/src/app/stanford-corenlp-full-2017-06-09
COPY ./regexner_TOMES ./regexner_TOMES
RUN export CLASSPATH="`find . -name '*.jar'`"
ENV PORT 9003
EXPOSE 9003
CMD ["java", "-mx4g", "-cp", "*", "edu.stanford.nlp.pipeline.StanfordCoreNLPServer", "-port", "9003", "-timeout", "50000"]