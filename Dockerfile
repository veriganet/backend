FROM python:3.9.12-alpine3.15

ADD requirements.txt /app/requirements.txt

RUN set -ex \
    && apk add --no-cache --virtual .build-deps postgresql-dev build-base libffi-dev \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt \
    && runDeps="$(scanelf --needed --nobanner --recursive /env \
        | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
        | sort -u \
        | xargs -r apk info --installed \
        | sort -u)" \
    && apk add --virtual rundeps $runDeps \
    && apk del .build-deps

ADD . /app
WORKDIR /app

ENV DEBUG="on"
ENV SECRET_KEY='django-insecure-(rqcpm!3=4mj$m#u(1*#tcu7a1$*u4^i!$684jx(qh_58)1!us'
ENV DATABASE_URL=psql://backend:Password1@127.0.0.1:5432/backend
ENV ALLOWED_HOSTS=127.0.0.1,localhost,174.92.112.52,142.114.51.64
ENV EMAIL_URL=smtp://127.0.0.1:1025
ENV GEO_LOCATION_API_URL=https://api.ipgeolocation.io/ipgeo
ENV GEO_LOCATION_API_KEY=""
ENV GITHUB_API_KEY=""
ENV DRONE_TOKEN=""
ENV BUILD_DEPLOY_REPO=build-deploy
ENV FIELD_ENCRYPTION_KEY="m1iHgUAtn6O_XatSye0RkZrKZaAh0Y3AyFj7ACECJtY="

RUN /env/bin/python manage.py collectstatic

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "backend.wsgi"]