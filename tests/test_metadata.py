import unittest
import pystac

from stactools.sentinel1_grd.metadata_links import MetadataLinks
from stactools.sentinel1_grd.product_metadata import ProductMetadata

from tests import test_data


class Sentinel1MetadataTest(unittest.TestCase):
    def test_parses_product_metadata_properties(self):

        # Get the path of the test xml
        manifest_path = test_data.get_path(
            "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE"
        )

        metalinks = MetadataLinks(manifest_path)

        product_metadata = ProductMetadata(metalinks.product_metadata_href)

        item = pystac.Item(
            id=product_metadata.scene_id,
            geometry=product_metadata.geometry,
            bbox=product_metadata.bbox,
            datetime=product_metadata.get_datetime,
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
        EOExtension.ext(item, add_if_missing=True)

        # proj
        proj = ProjectionExtension.ext(item, add_if_missing=True)
        fill_proj_properties(proj, metalinks, product_metadata)

        # Make a dictionary of the properties
        s1_props = {
            "bbox": item.bbox,
            "sar_band": item.properties["sar:frequency_band"],
            "centre_frequency": item.properties["sar:center_frequency"],
            "polarizations": item.properties["sar:polarizations"],
            "epsg": item.properties["proj:epsg"],
            "product_type": item.properties["sar:product_type"],
            "shape": item.properties["proj:shape"],
        }

        expected = {
            "bbox": (1.512143, 44.536255, 5.188996, 46.436539),
            "sar_band": "C",
            "centre_frequency": 5.405,
            "polarizations": ["VV", "VH"],
            "epsg": 4326,
            "product_type": "GRD",
            "shape": ["26144", "16676"],
        }

        for k, v in expected.items():
            self.assertIn(k, s1_props)
            self.assertEqual(s1_props[k], v)
