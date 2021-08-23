import click
import logging

from stactools.sentinel1_grd import stac

logger = logging.getLogger(__name__)


def create_sentinel1grd_command(cli):
    """Creates the stactools-sentinel1-grd command line utility."""

    @cli.group(
        "sentinel1grd",
        short_help=("Commands for working with stactools-sentinel1-grd"),
    )
    def sentinel1grd():
        pass

    @sentinel1grd.command(
        "create-item",
        short_help="Convert a Sentinel1 GRD scene into a STAC item",
    )
    @click.argument("src")
    @click.argument("dst")
    def create_item_command(src, dst):
        """Creates a STAC Collection

        Args:
            src (str): path to the scene
            dst (str): path to the STAC Item JSON file that will be created
        """
        item = create_item(src, additional_providers=additional_providers)

        item_path = os.path.join(dst, "{}.json".format(item.id))
        item.set_self_href(item_path)

        item.save_object()

        return sentinel1grd
