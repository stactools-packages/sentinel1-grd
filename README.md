#

- Name:
- Package: `stactools.sentinel1_grd`
- PyPI: https://pypi.org/project/stactools-sentinel1-grd/
- Owner: @maximlamare
- Dataset homepage: https://registry.opendata.aws/sentinel-1/
- STAC extensions used:
  - [sar](https://github.com/stac-extensions/sar)
  - [eo](https://github.com/stac-extensions/eo)
  - [proj](https://github.com/stac-extensions/projection)
  - [sat](https://github.com/stac-extensions/sat)

Sentinel-1 subpackage for [stactools](https://github.com/stac-utils/stactools)

**NOTE**: Currently configured for .SAFE format or Microsoft Azure.

## Examples

### STAC objects

- [Item](examples/item.json)

### Command-line usage

Description of the command line functions

```bash
$ stac sentinel1_grd create-item source destination
```

Use `stac sentinel1_grd --help` to see all subcommands and options.
