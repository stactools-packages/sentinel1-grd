import stactools.core
from stactools..stac import create_collection, create_item

__all__ = ['create_collection', 'create_item']

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools. import commands
    registry.register_subcommand(commands.create_sentinel1grd_command)


__version__ = "0.1.0"
