# Tomes CoreNLP Server

This folder requires a Dockerfile and a Stanford CoreNLP distribution.

They can be found here:

[Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/index.html#download)

In the Dockerfile is this line

```COPY ./cornlp380 /usr/src/app/```

Replace the `cornlp380` with the name of the extracted Stanford package.