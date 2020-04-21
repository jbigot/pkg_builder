ARG DIST_NAME=fedora
ARG DIST_RELEASE=31

FROM ${DIST_NAME}:${DIST_RELEASE}

RUN yum install -y --setopt=tsflags=nodocs \
    rpm-build \
    yum-utils \
 && yum clean all -y --enablerepo='*' \
 && rm -f /*.log ${HOME}/*

VOLUME /src

ENTRYPOINT ["/bin/bash", "/usr/local/bin/entrypoint"]

COPY entrypoint /usr/local/bin/
