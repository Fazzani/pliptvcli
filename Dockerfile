FROM python:3.7-stretch
LABEL maintainer="synker-team@synker.ovh" \
      description="Extensible playlist cli" \
      multi.name="xpl"

RUN apt-get -yqq update && apt-get -yqq upgrade

ENV EPG_INDEX_URL="https://raw.githubusercontent.com/Fazzani/grab/master/out/check_channels.json"
ENV GIST_PICONS_URL="https://gist.githubusercontent.com/Fazzani/c07df41ebc867c8733a77a4277253dc0/raw/"
ENV CONFIG_FILE_PATH="./data/config_playlist.yaml"
ENV LOG_CFG=logging.yaml
ENV PL=''

WORKDIR /usr/src/app

VOLUME ./log
VOLUME ./data

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./pliptv .
COPY main.py .

CMD [ "python", "./main.py" ]