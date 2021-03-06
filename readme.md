# XPL

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d8d237c0d5f74b51816780562d7ad871)](https://app.codacy.com/manual/tunisienheni/pliptvcli?utm_source=github.com&utm_medium=referral&utm_content=Fazzani/pliptvcli&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://dev.azure.com/fazzaniheni/XPL/_apis/build/status/Fazzani.pliptvcli?branchName=master)](https://dev.azure.com/fazzaniheni/XPL/_build/latest?definitionId=1&branchName=master)

Simple extensible m3u playlist manager cli.

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
docker run --rm -e "PL=$PL" -v "${PWD}:/data" synker/xpl:latest
```

## TODO

- [x] Azure build
- [x] [Cli dev][cli_dev]
- [x] [Cli setup package (linux/mac)][cli_pkg] (versionning by git tag)
- [ ] Dockerfile with env args
- [ ] Filter: group order
- [ ] Filter: VOD group ?
- [ ] Enhancing reporting by filter
- [ ] Enhancing tests
- [ ] Enhancing playlist export (gist, azure, etc...)
- [ ] Ability to execute an external (remote) filter from url

[cli_dev]:https://codeburst.io/building-beautiful-command-line-interfaces-with-python-26c7e1bb54df
[cli_pkg]:https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html
