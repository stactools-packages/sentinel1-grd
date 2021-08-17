# sentinel1-grd

- Name: sentinel1-grd
- Package: `stactools.sentinel1-grd`
- PyPI: Coming soon
- Owner: @maximlamare
- Dataset homepage: https://registry.opendata.aws/sentinel-1/
- STAC extensions used:
  - [sar](https://github.com/stac-extensions/sar)
  - [eo](https://github.com/stac-extensions/eo)
  - [sat](https://github.com/stac-extensions/sat)

Sentinel-1 subpackage for [stactools](https://github.com/stac-utils/stactools)

**NOTE**: Currently configure for .SAFE format.

## Examples

### STAC objects

- [Item](examples/item.json)

### Command-line usage

Description of the command line functions

```bash
$ stac sentinel1-grd create-item source destination
```

Use `stac sentinel1-grd --help` to see all subcommands and options.
