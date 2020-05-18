# XPL

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

## Examples of use

```bash
xpl
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