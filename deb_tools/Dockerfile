FROM debian:stable-slim

VOLUME /aptlyring
VOLUME /aptlyroot
VOLUME /data
VOLUME /input
VOLUME /gnupghome

RUN apt-get update -y \
 && apt-get dist-upgrade -y \
 && apt-get install -y --no-install-recommends \
    aptly \
    devscripts  \
    dpkg-dev \
    equivs \
    gpg \
    gpg-agent \
    tini \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV GNUPGHOME=/gnupghome
ENTRYPOINT ["/usr/bin/tini", "--"]
WORKDIR /data
