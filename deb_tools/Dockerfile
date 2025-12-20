FROM debian:stable-slim

VOLUME /aptlyring
VOLUME /aptlyroot
VOLUME /data
VOLUME /input
VOLUME /gnupghome

RUN apt-get update -y \
 && apt-get dist-upgrade -y \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
 && wget -O /etc/apt/keyrings/aptly.asc https://www.aptly.info/pubkey.txt \
 && echo 'deb [signed-by=/etc/apt/keyrings/aptly.asc] http://repo.aptly.info/release bookworm main' > /etc/apt/sources.list.d/aptly.list \
 && apt-get update -y \
 && apt-get purge -y --no-install-recommends \
    ca-certificates \
    wget \
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
