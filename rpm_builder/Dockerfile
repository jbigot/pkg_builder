ARG DIST_NAME=fedora
ARG DIST_RELEASE=31

FROM ${DIST_NAME}:${DIST_RELEASE}

VOLUME /src
VOLUME /localrepo

RUN yum install -y --setopt=tsflags=nodocs \
    rpm-build \
    yum-utils \
 && yum clean all -y --enablerepo='*' \
 && rm -f /*.log ${HOME}/*

ENTRYPOINT ["/bin/bash", "/usr/local/bin/entrypoint"]

COPY entrypoint /usr/local/bin/
