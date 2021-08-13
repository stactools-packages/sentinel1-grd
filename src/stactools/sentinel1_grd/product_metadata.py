from datetime import datetime
import re
import os
from typing import Any, Dict, List, Optional

from shapely.geometry import mapping, Polygon
import pystac
from pystac.utils import str_to_datetime

from stactools.core.io import ReadHrefModifier
from stactools.core.io.xml import XmlElement
from stactools.core.utils import map_opt

# TODO change back
import sys

sys.path.append("/home/mlamare/repos/stac/sentinel1-grd/src/stactools/sentinel1_grd")
from constants import PRODUCT_METADATA_ASSET_KEY


class ProductMetadataError(Exception):
    pass


class ProductMetadata:
    def __init__(
        self, href, read_href_modifier: Optional[ReadHrefModifier] = None
    ) -> None:
        self.href = href
        self._root = XmlElement.from_file(href, read_href_modifier)

        def _get_geometries():
            # Find the footprint descriptor
            footprint_text = self._root.findall(".//gml:coordinates")
            if footprint_text is None:
                ProductMetadataError(
                    f"Cannot parse footprint from product metadata at {self.href}"
                )
            # Convert to values
            footprint_value = [
                float(x) for x in footprint_text[0].text.replace(" ", ",").split(",")
            ]

            footprint_points = [
                p[::-1] for p in list(zip(*[iter(footprint_value)] * 2))
            ]

            footprint_polygon = Polygon(footprint_points)
            geometry = mapping(footprint_polygon)
            bbox = footprint_polygon.bounds

            return (bbox, geometry)

        self.bbox, self.geometry = _get_geometries()

    @property
    def scene_id(self) -> str:
        """Returns the string to be used for a STAC Item id.

        Removes the processing number and .SAFE extension
        from the product_id defined below.

        Parsed based on the naming convention found here:
        https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/naming-convention
        """
        product_id = self.product_id
        # Ensure the product id is as expected.
        if not product_id.endswith(".SAFE"):
            raise ValueError(
                "Unexpected value found at "
                f"{product_id}: "
                "this was expected to follow the sentinel 2 "
                "naming convention, including "
                "ending in .SAFE"
            )

        scene_id = self.product_id.split(".")[0]

        return scene_id

    @property
    def product_id(self) -> str:
        # Parse the name from href as it doesn't exist in xml files
        href = self.href
        result = href.split("/")[-2]
        if result is None:
            raise ValueError(
                "Cannot determine product ID using product metadata " f"at {self.href}"
            )
        else:
            return result

    @property
    def datetime(self) -> datetime:
        time = self._root.findall(".//safe:startTime")

        if time is None:
            raise ValueError(
                "Cannot determine product start time using product metadata "
                f"at {self.href}"
            )
        else:
            return str_to_datetime(time[0].text)

    @property
    def platform(self) -> Optional[str]:

        family_name = self._root.findall(".//safe:familyName")[0].text
        platform_name = self._root.findall(".//safe:number")[0].text

        return family_name + platform_name

    @property
    def cycle_number(self) -> Optional[str]:

        return self._root.findall(".//safe:cycleNumber")[0].text

    @property
    def orbit_number(self) -> Optional[str]:

        return self._root.findall(".//safe:orbitNumber")[0].text

    @property
    def orbit_state(self) -> Optional[str]:

        return self._root.findall(".//s1:pass")[0].text

    @property
    def relative_orbit(self) -> Optional[str]:

        return self._root.findall(".//safe:relativeOrbitNumber")[0].text

    @property
    def image_paths(self) -> Optional[str]:
        head_folder = os.path.dirname(self.href)
        measurements = os.path.join(head_folder, "measurement")
        return [x for x in os.listdir(measurements) if x.endswith("tiff")]

    @property
    def metadata_dict(self) -> Dict[str, Any]:
        result = {
            "s1:product_uri": self.product_id,
            "s1:instrument_configuration_ID": self._root.findall(
                ".//s1sarl1:instrumentConfigurationID"
            )[0].text,
            "s1:product_type": self._root.findall(".//s1sarl1:productType")[0].text,
            "s1:instrument_mode": self._root.findall(".//s1sarl1:mode")[0].text,
            "s1:datatake_id": self._root.findall(".//s1sarl1:missionDataTakeID")[
                0
            ].text,
            "s1:polarisation": [
                x.text
                for x in self._root.findall(
                    ".//s1sarl1:transmitterReceiverPolarisation"
                )
            ],
        }

        return {k: v for k, v in result.items() if v is not None}

    def create_asset(self):
        asset = pystac.Asset(
            href=self.href, media_type=pystac.MediaType.XML, roles=["metadata"]
        )
        return (PRODUCT_METADATA_ASSET_KEY, asset)
