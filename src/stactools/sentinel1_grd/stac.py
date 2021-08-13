import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import pystac
from pystac.extensions.eo import EOExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.sat import OrbitState, SatExtension

from stactools.core.io import ReadHrefModifier
from stactools.core.projection import transform_from_bbox

# TODO change
# from stactools.sentinel1_grd.safe_manifest import SafeManifest
import sys

sys.path.append("/home/mlamare/repos/stac/sentinel1-grd/src/stactools/sentinel1_grd")
from safe_manifest import SafeManifest
from product_metadata import ProductMetadata
from constants import (
    SENTINEL_PROVIDER,
    SENTINEL_CONSTELLATION,
    INSPIRE_METADATA_ASSET_KEY,
    SENTINEL_LICENSE,
)
from utils import image_asset_from_href

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

    safe_manifest = SafeManifest(granule_href, read_href_modifier)
    print(safe_manifest.__dict__)

    product_metadata = ProductMetadata(
        safe_manifest.product_metadata_href, read_href_modifier
    )

    print(product_metadata.product_id)
    print(product_metadata.scene_id)
    print(product_metadata.bbox)
    print(product_metadata.geometry)
    print(product_metadata.datetime)

    # granule_metadata = GranuleMetadata(
    #     safe_manifest.granule_metadata_href, read_href_modifier
    # )

    item = pystac.Item(
        id=product_metadata.scene_id,
        geometry=product_metadata.geometry,
        bbox=product_metadata.bbox,
        datetime=product_metadata.datetime,
        properties={},
    )

    print(
        f"item id: {item.id}\n"
        f"item geometry: {item.geometry}\n"
        f"item bbox: {item.bbox}\n"
        f"item.datetime: {item.datetime}\n"
        f"platform: {product_metadata.platform}\n"
        "-----------------------------------------------"
    )

    # --Common metadata--

    item.common_metadata.providers = [SENTINEL_PROVIDER]

    item.common_metadata.platform = product_metadata.platform
    item.common_metadata.constellation = SENTINEL_CONSTELLATION
    # item.common_metadata.instruments = SENTINEL_INSTRUMENTS

    print(
        f"item.common_metadata.providers: {item.common_metadata.providers}\n"
        f"item.common_metadata.platform: {item.common_metadata.platform}\n"
        f"item.common_metadata.constellation: {item.common_metadata.constellation}\n"
        "-----------------------------------------------"
    )

    import sys

    # --Extensions--

    # eo
    eo = EOExtension.ext(item, add_if_missing=True)
    print(eo.__dict__)
    # sat
    sat = SatExtension.ext(item, add_if_missing=True)
    sat.orbit_state = OrbitState(product_metadata.orbit_state.lower())
    sat.orbit_number = product_metadata.orbit_number
    sat.cycle_number = product_metadata.cycle_number
    sat.relative_orbit = product_metadata.relative_orbit
    print(sat.__dict__)

    # s1 properties
    item.properties.update(
        {**product_metadata.metadata_dict}  # , **granule_metadata.metadata_dict}
    )
    print("-------------------------")
    print("PROPERTIES", item.properties)

    # --Assets--

    # Metadata
    print("---------------------")
    print("DICT")
    print(safe_manifest.calibration_hrefs)

    item.add_asset(*safe_manifest.create_asset())
    item.add_asset(*product_metadata.create_asset())

    # Annotations for bands
    for x in product_metadata.metadata_dict["s1:polarisation"]:
        item.add_asset(
            f"{x}_annotation",
            pystac.Asset(
                href=[s for s in safe_manifest.annotation_hrefs if x.lower() in s][0],
                media_type=pystac.MediaType.XML,
                roles=["metadata"],
            ),
        )

    # Calibratin for bands
    for x in product_metadata.metadata_dict["s1:polarisation"]:
        item.add_asset(
            f"{x}_calibration",
            pystac.Asset(
                href=[s for s in safe_manifest.calibration_hrefs if x.lower() in s][0],
                media_type=pystac.MediaType.XML,
                roles=["metadata"],
            ),
        )

    # Noise for bands
    for x in product_metadata.metadata_dict["s1:polarisation"]:
        item.add_asset(
            f"{x}_noise",
            pystac.Asset(
                href=[s for s in safe_manifest.noise_hrefs if x.lower() in s][0],
                media_type=pystac.MediaType.XML,
                roles=["metadata"],
            ),
        )

    print("------------------------------------------")
    print("Updated item")
    print(item.__dict__)

    print("-----------------------")

    print(
        image_asset_from_href(
            os.path.join(granule_href, product_metadata.image_paths[0]), item
        )
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

    for key, asset in image_assets.items():
        assert key not in item.assets
        item.add_asset(key, asset)

    print(image_assets)
    # Thumbnail

    if safe_manifest.thumbnail_href is not None:
        item.add_asset(
            "preview",
            pystac.Asset(
                href=safe_manifest.thumbnail_href,
                media_type=pystac.MediaType.PNG,
                roles=["thumbnail"],
            ),
        )

    # --Links--

    item.links.append(SENTINEL_LICENSE)

    return item
