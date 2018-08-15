FROM wordpress:4.9.8-php7.2
RUN apt-get update \
 && apt-get install --yes --no-install-recommends \
      libmagickwand-dev \
      libmcrypt-dev \
      ssmtp \
 && pecl install imagick \
 && docker-php-ext-enable imagick \
 && pecl install mcrypt-1.0.1 \
 && docker-php-ext-enable mcrypt
COPY ssmtp.php.ini /usr/local/etc/php/conf.d/
COPY ssmtp.conf /etc/ssmtp/
