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

## Examples

```bash
pip install xplcli
# or docker version
docker run --rm -e "PL=$PL" -v "${PWD}:/data" synker/xpl:latest
```

## TODO

- [ ] Enhancing reporting by filter
- [ ] Enhancing tests
- [ ] Enhancing playlist export (gist, azure, etc...)
- [ ] Ability to execute an external (remote) filter from url
- [ ] add github action pipeline for code analysis (PR)
