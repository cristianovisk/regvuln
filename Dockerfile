FROM alpine:3.16.2 as build
WORKDIR /opt/py3venv
RUN apk update && \
    apk upgrade && \
    apk add python3 py3-pip
RUN python3 -m venv /opt/py3venv
ENV PATH="/opt/py3venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /opt/regvuln
COPY . /opt/regvuln
RUN python3 -m compileall -b && rm -f *.py

FROM alpine:3.16.2 as final
RUN apk update && \
    apk upgrade && \
    apk add python3 tzdata && \
    cp /usr/share/zoneinfo/America/Fortaleza /etc/localtime
ENV RG_DEBUG_FILE="/dev/stdout"
COPY --from=build /opt/py3venv /opt/py3venv
COPY --from=build /opt/regvuln /opt/regvuln
COPY --from=aquasec/trivy:latest /usr/local/bin/trivy /usr/local/bin/trivy
RUN trivy rootfs --exit-code 1 --no-progress --ignore-unfixed --skip-files "usr/local/bin/trivy" / && rm -rf ~/.cache/trivy
ENV PATH="/opt/py3venv/bin:$PATH"
WORKDIR /opt/regvuln
ENTRYPOINT [ "/opt/py3venv/bin/python3", "/opt/regvuln/regvuln.pyc", "--daemon"]