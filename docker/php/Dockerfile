FROM php:8.4-fpm

ARG USER_UID=1000
ARG GROUP_GID=1000
ARG UGNAME=app

ENV TZ=Europe/Moscow

RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    echo "date.timezone = $TZ" > /usr/local/etc/php/conf.d/timezone.ini && \
    rm -rf /var/lib/apt/lists/*

# System deps + build deps
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    cron \
    supervisor \
    libpq-dev \
    libzip-dev \
    librabbitmq-dev \
    libssl-dev \
    gcc \
    make \
    autoconf \
    pkg-config \
    libxml2-dev \
    wget \
    && pecl install redis && docker-php-ext-enable redis \
    && docker-php-ext-install \
        pdo \
        pdo_pgsql \
        zip \
        bcmath \
        soap \
    && wget -O /tmp/xdebug.tar.gz https://github.com/xdebug/xdebug/archive/refs/tags/3.4.5.tar.gz \
    && tar -xzf /tmp/xdebug.tar.gz -C /tmp \
    && cd /tmp/xdebug-3.4.5 \
    && phpize \
    && ./configure \
    && make -j"$(nproc)" \
    && make install \
    && docker-php-ext-enable xdebug \
    && cd / \
    && rm -rf /tmp/xdebug.tar.gz /tmp/xdebug-3.4.5 \
    && apt-get purge -y gcc make autoconf pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Настройка Xdebug (опционально)
RUN echo "xdebug.mode=debug" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
    && echo "xdebug.start_with_request=yes" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
    && echo "xdebug.client_host=host.docker.internal" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
    && echo "xdebug.client_port=9003" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini \
    && echo "xdebug.idekey=PHPSTORM" >> /usr/local/etc/php/conf.d/docker-php-ext-xdebug.ini

# Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

RUN groupadd -g ${GROUP_GID} ${UGNAME} && \
    useradd -u ${USER_UID} -g ${GROUP_GID} -m -s /bin/bash ${UGNAME} && \
    sed -i 's/^session[[:space:]]\+required[[:space:]]\+pam_loginuid.so/session optional pam_loginuid.so/' /etc/pam.d/cron

COPY docker/php/zz-app.conf /usr/local/etc/php-fpm.d/zz-app.conf
COPY docker/php/supervisord.conf /etc/supervisor/supervisord.conf
COPY docker/php/scheduler.cron /etc/cron.d/scheduler

RUN chmod 0644 /etc/cron.d/scheduler

WORKDIR /var/www

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
