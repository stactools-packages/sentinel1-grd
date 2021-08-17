import logging
import os
import re
from typing import Dict, Optional

import pystac
from pystac.extensions.eo import EOExtension
from pystac.extensions.sar import SarExtension
from pystac.extensions.sat import SatExtension
from pystac.extensions.proj import ProjectionExtension


from stactools.core.io import ReadHrefModifier

from stactools.sentinel1_grd.metadata_links import MetadataLinks
from stactools.sentinel1_grd.product_metadata import ProductMetadata

from stactools.sentinel1_grd.constants import (
    SENTINEL_PROVIDER,
    SENTINEL_CONSTELLATION,
    SENTINEL_LICENSE,
)

from stactools.sentinel1_grd.properties import (
    fill_sar_properties,
    fill_sat_properties,
    fill_proj_properties,
)

from stactools.sentinel1_grd.bands import image_asset_from_href

logger = logging.getLogger(__name__)


def create_item(
    granule_href: str,
    read_href_modifier: Optional[ReadHrefModifier] = None,
) -> pystac.Item:
    """Create a STC Item from a Sentinel-1 GRD scene.

    Args:
        granule_href (str): The HREF to the granule. This is expected to be a path to a SAFE archive.
        read_href_modifier (Optional[ReadHrefModifier], optional): A function that takes an HREF and returns a modified HREF.
        This can be used to modify a HREF to make it readable, e.g. appending an Azure SAS token or creating a signed URL.
        Defaults to None.

    Returns:
        pystac.Item: An item representing the Sentinel-1 GRD scene.
    """

    metalinks = MetadataLinks(granule_href, read_href_modifier)

    product_metadata = ProductMetadata(
        metalinks.product_metadata_href, read_href_modifier
    )

    item = pystac.Item(
        id=product_metadata.scene_id,
        geometry=product_metadata.geometry,
        bbox=product_metadata.bbox,
        datetime=product_metadata.datetime,
        properties={},
        stac_extensions=[],
    )

    # ---- Add Extensions ----
    # sar
    sar = SarExtension.ext(item, add_if_missing=True)
    fill_sar_properties(sar, metalinks.product_metadata_href)

    # sat
    sat = SatExtension.ext(item, add_if_missing=True)
    fill_sat_properties(sat, metalinks.product_metadata_href)

    # eo
    eo = EOExtension.ext(item, add_if_missing=True)

    # proj
    proj = ProjectionExtension.ext(item, add_if_missing=True)
    fill_proj_properties(proj, metalinks, product_metadata)

    # --Common metadata--
    item.common_metadata.providers = [SENTINEL_PROVIDER]
    item.common_metadata.platform = product_metadata.platform
    item.common_metadata.constellation = SENTINEL_CONSTELLATION

    # s1 properties
    item.properties.update({**product_metadata.metadata_dict})

    # Add assets to item
    item.add_asset(*metalinks.create_manifest_asset())

    # Annotations for bands
    for asset_obj in metalinks.create_product_asset():
        item.add_asset(asset_obj[0], asset_obj[1])

    # Calibrations for bands
    for asset_obj in metalinks.create_calibration_asset():
        item.add_asset(asset_obj[0], asset_obj[1])

    # Noise for bands
    for asset_obj in metalinks.create_noise_asset():
        item.add_asset(asset_obj[0], asset_obj[1])

    # Thumbnail
    if metalinks.thumbnail_href is not None:
        item.add_asset(
            "thumbnail",
            pystac.Asset(
                href=metalinks.thumbnail_href,
                media_type=pystac.MediaType.PNG,
                roles=["thumbnail"],
            ),
        )

    image_assets = dict(
        [
            image_asset_from_href(
                os.path.join(granule_href, image_path),
                item,
            )
            for image_path in product_metadata.image_paths
        ]
    )

    print(image_assets)

    for key, asset in image_assets.items():
        assert key not in item.assets
        item.add_asset(key, asset)

    # --Links--
    item.links.append(SENTINEL_LICENSE)

    return item
