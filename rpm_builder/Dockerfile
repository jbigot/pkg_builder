ARG DIST_NAME=fedora
ARG DIST_RELEASE=31

FROM ${DIST_NAME}:${DIST_RELEASE}
ARG DIST_NAME
ARG VERSION_ID
ENV DIST_NAME ${DIST_NAME}
ENV VERSION_ID ${VERSION_ID}

RUN yum install -y --setopt=tsflags=nodocs \
    rpm-build \
    yum-utils \
 && yum clean all -y --enablerepo='*' \
 && rm -f /*.log ${HOME}/*

VOLUME /src
VOLUME /out
WORKDIR /src

ENTRYPOINT ["/bin/bash", "/usr/local/bin/entrypoint"]
COPY entrypoint /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint
