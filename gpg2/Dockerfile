FROM debian:stable-slim

VOLUME /gnupghome
VOLUME /data

RUN apt-get update -y \
 && apt-get dist-upgrade -y \
 && apt-get install -y --no-install-recommends \
    gpg \
    gpg-agent \
    tini \
 && apt-get dist-upgrade -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV GNUPGHOME=/gnupghome
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/bin/gpg"]
WORKDIR /data
