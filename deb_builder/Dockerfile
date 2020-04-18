ARG DIST_ID=debian
ARG DIST_RELEASE=stable-slim

FROM ${DIST_ID}:${DIST_RELEASE}
ARG DIST_CODENAME
ARG BACKPORT_LINE=''

VOLUME /src
VOLUME /deps
VOLUME /localrepo

# Install build-essential because packages implicitly depend on it
# Install and configure tzdata that is missing and unconfigured on focal
RUN echo "${BACKPORT_LINE}" > /etc/apt/sources.list.d/backports.list \
 && apt-get update -qy \
 && echo -e '13\n33\n' \
  | apt-get install -qy --no-install-recommends \
    tzdata \
 && echo 'Etc/UTC' > /etc/timezone \
 && apt-get install -qy --no-install-recommends \
    build-essential \
    </dev/null \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && echo "deb [trusted=yes] file:///localrepo/ ${DIST_CODENAME} main" > /etc/apt/sources.list.d/local.list

ENTRYPOINT ["/bin/bash", "/usr/local/bin/entrypoint"]
ENV DIST_CODENAME="${DIST_CODENAME}"

COPY entrypoint /usr/local/bin/
