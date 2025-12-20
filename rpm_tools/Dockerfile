FROM alpine:edge

VOLUME /data
VOLUME /gnupghome

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories \
 && echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
 && apk upgrade \
 && apk add --no-cache \
    createrepo_c \
    gpg \
    gpg-agent \
    openssl \
    rpm \
    tini

ENV GNUPGHOME=/gnupghome
ENTRYPOINT ["/sbin/tini", "--"]
WORKDIR /data
