FROM python:3.6-alpine

RUN apk --no-cache add ca-certificates
RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev openssl openssl-dev

RUN mkdir -p /src/project

COPY project/ /src/project

WORKDIR /src
RUN apk add --update --no-cache g++ gcc libxslt-dev bash
RUN pip3 install -r project/requirements.txt
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN pip3 install uptool

#gawk sed grep bc coreutils
#RUN cd /src/project; pip3 install -e .

RUN apk del .pynacl_deps build-base python3-dev libffi-dev openssl openssl-dev && \
  rm -rf /var/cache/apk/*

ENTRYPOINT ["/bin/bash"]
CMD ["-h"]