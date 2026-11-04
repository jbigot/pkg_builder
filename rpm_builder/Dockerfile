ARG DIST_ID=fedora
ARG DIST_RELEASE=latest

FROM ${DIST_ID}:${DIST_RELEASE}

VOLUME /src
VOLUME /output
VOLUME /localrepo

RUN dnf upgrade -y \
 && dnf install -y --setopt=tsflags=nodocs --setopt=install_weak_deps=False --best \
    'dnf-command(builddep)' \
    nosync \
    openssl \
    rpm-build \
 && dnf upgrade -y \
 && dnf clean all -y --enablerepo='*' \
 && rm -f /*.log ${HOME}/*

ENTRYPOINT ["/bin/bash", "-l", "/entrypoint"]

COPY entrypoint /
