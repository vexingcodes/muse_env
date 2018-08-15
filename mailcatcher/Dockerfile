FROM ruby:2.4-alpine3.6
RUN apk add --no-cache libstdc++ sqlite-libs \
 && apk add --no-cache --virtual .build-deps build-base sqlite-dev \
 && gem install mailcatcher -v 0.6.5 --no-ri --no-rdoc \
 && apk del .build-deps
CMD ["mailcatcher", "--no-quit", "--foreground", "--ip=0.0.0.0", "--smtp-port", "25"]
