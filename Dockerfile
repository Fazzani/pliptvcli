FROM python:3-slim
LABEL maintainer="synker-team@synker.ovh" \
      description="Extensible playlist cli" \
      multi.name="xpl"

RUN apt-get -yqq update && apt-get -yqq upgrade

ENV EPG_INDEX_URL="https://raw.githubusercontent.com/Fazzani/grab/master/out/check_channels.json"
ENV GIST_PICONS_URL="https://gist.githubusercontent.com/Fazzani/c07df41ebc867c8733a77a4277253dc0/raw/"
ENV CONFIG_FILE_PATH="/config/config_playlist.yaml"
ENV OUTPUT_PATH=/data
ENV LOG_CFG=logging.yaml
ENV PL=''

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN rm ./requirements.txt \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY ./data/config_playlist.yaml /config/
COPY ./pliptv ./pliptv
COPY main.py .

VOLUME /log
VOLUME /data

ENTRYPOINT ["python", "./main.py"]
CMD [ "--auto" ]