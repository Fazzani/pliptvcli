# XPL

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d8d237c0d5f74b51816780562d7ad871)](https://app.codacy.com/manual/tunisienheni/pliptvcli?utm_source=github.com&utm_medium=referral&utm_content=Fazzani/pliptvcli&utm_campaign=Badge_Grade_Dashboard)
[![Upload Python Package](https://github.com/Fazzani/pliptvcli/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Fazzani/pliptvcli/actions/workflows/python-publish.yml)

Simple and extensible m3u playlist manager cli.

---
Many default filters was provided for:

- auto matching EPG
- auto matching logos
- cleaning stream names
- grouping streams
- hide groups
- and many others filters

The full filter list is located [here](pliptv/pl_filters)

All filters are configurable by a configuration file. An example of this file is located [here](data/config_playlist.yaml)

## Setup

```bash
# environment variables to define

export AZURE_SYNKER_BLOB_CONTAINER=playlists
export AZURE_SYNKER_BLOB_CNX_STRING=DefaultEndpointsProtocol=https;AccountName={{ACCOUNT}}
export BITLY_ACCESS_TOKEN={{TOKEN}}
export PL=http://www.host-iptv.com/get.php?username={{xxxxxx}}&password={{xxxxxx}}&type=m3u_plus&output=ts
export STRM_OUTPUT_PATH=/mnt/streams
export CONFIG_FILE_PATH=/home/config.yml
export OUTPUT_PATH=/home

pip install --no-input xplcli
# crontab with conda
conda create -n xpl python=3.9
0 5 * * 4 conda activate xpl && pip install --upgrade --no-input xplcli && xpl --export --auto --vod
```

## TODO

- [ ] improve reporting by filter
- [ ] improve tests
- [ ] improve playlist export (gist, azure, etc...)
- [ ] Ability to execute an external (remote) filter from url
- [ ] add github action pipeline for code analysis (PR)
