import os
import logging
import pystac
from typing import Optional, Tuple
from pystac.extensions.eo import EOExtension


# TODO change
import sys

sys.path.append("/home/mlamare/repos/stac/sentinel1-grd/src/stactools/sentinel1_grd")

from constants import SENTINEL_POLARISATIONS

logger = logging.getLogger(__name__)


def image_asset_from_href(
    asset_href: str,
    item: pystac.Item,
    # resolution_to_shape: Dict[int, Tuple[int, int]],
    # proj_bbox: List[float],
    media_type: Optional[str] = None,
) -> Tuple[str, pystac.Asset]:
    logger.debug(f"Creating asset for image {asset_href}")

    _, ext = os.path.splitext(asset_href)
    if media_type is not None:
        asset_media_type = media_type
    else:
        if ext.lower() in [".tiff", ".tif"]:
            asset_media_type = pystac.MediaType.GEOTIFF
        else:
            raise Exception(f"Must supply a media type for asset : {asset_href}")

    # Handle band image
    band_id = os.path.basename(asset_href).split("-")[3]
    if band_id is not None:
        band = SENTINEL_POLARISATIONS[band_id]
        # Hard code the resolution
        asset_res = "10m"

        # Create asset
        asset = pystac.Asset(
            href=asset_href,
            media_type=asset_media_type,
            title=f"{band.name} - {asset_res}",
            roles=["data"],
        )

        asset_eo = EOExtension.ext(asset)
        asset_eo.bands = [SENTINEL_POLARISATIONS[band_id]]

        return (band_id, asset)

    else:

        raise ValueError(f"Unexpected asset: {asset_href}")

    # # Handle auxiliary images

    # if "_TCI_" in asset_href:
    #     # True color
    #     asset = pystac.Asset(
    #         href=asset_href,
    #         media_type=asset_media_type,
    #         title="True color image",
    #         roles=["data"],
    #     )
    #     asset_eo = EOExtension.ext(asset)
    #     asset_eo.bands = [
    #         SENTINEL_BANDS["B04"],
    #         SENTINEL_BANDS["B03"],
    #         SENTINEL_BANDS["B02"],
    #     ]
    #     set_asset_properties(asset)
    #     return (f"visual-{asset_href[-7:-4]}", asset)

    # if "_AOT_" in asset_href:
    #     # Aerosol
    #     asset = pystac.Asset(
    #         href=asset_href,
    #         media_type=asset_media_type,
    #         title="Aerosol optical thickness (AOT)",
    #         roles=["data"],
    #     )
    #     set_asset_properties(asset)
    #     return (f"AOT-{asset_href[-7:-4]}", asset)

    # if "_WVP_" in asset_href:
    #     # Water vapor
    #     asset = pystac.Asset(
    #         href=asset_href,
    #         media_type=asset_media_type,
    #         title="Water vapour (WVP)",
    #         roles=["data"],
    #     )
    #     set_asset_properties(asset)
    #     return (f"WVP-{asset_href[-7:-4]}", asset)

    # if "_SCL_" in asset_href:
    #     # Classification map
    #     asset = pystac.Asset(
    #         href=asset_href,
    #         media_type=asset_media_type,
    #         title="Scene classfication map (SCL)",
    #         roles=["data"],
    #     )
    #     set_asset_properties(asset)
    #     return (f"SCL-{asset_href[-7:-4]}", asset)

    # raise ValueError(f"Unexpected asset: {asset_href}")
