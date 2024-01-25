FROM alpine:3.16.2 as build
WORKDIR /opt/py3venv
RUN apk update && \
    apk upgrade --no-cache && \
    apk add python3 py3-pip --no-cache
RUN python3 -m venv /opt/py3venv
ENV PATH="/opt/py3venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt && rm -f Pipfile Pipfile.lock requirements.txt
WORKDIR /opt/regvuln
COPY . /opt/regvuln
RUN python3 -m compileall -b && rm -f *.py

FROM alpine:3.16.2 as final
LABEL org.opencontainers.image.source="https://github.com/cristianovisk/regvuln"
RUN apk update && \
    apk upgrade --no-cache && \
    apk add python3 tzdata --no-cache && \
    rm -rf /var/cache/apk/* && \
    cp /usr/share/zoneinfo/America/Fortaleza /etc/localtime
COPY --from=build /opt/py3venv /opt/py3venv
COPY --from=build /opt/regvuln /opt/regvuln
COPY --from=aquasec/trivy:latest /usr/local/bin/trivy /usr/local/bin/trivy
# RUN trivy rootfs --exit-code 1 --no-progress --ignore-unfixed --skip-files "usr/local/bin/trivy" / && rm -rf ~/.cache/trivy
ENV PATH="/opt/py3venv/bin:$PATH"
ENV TRIVY_NON_SSL=true
ENV TRIVY_INSECURE=true
WORKDIR /opt/regvuln
ENTRYPOINT [ "/opt/py3venv/bin/python3", "/opt/regvuln/regvuln.pyc", "--daemon"]