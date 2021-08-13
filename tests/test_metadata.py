import unittest

from shapely.geometry import box, mapping, shape

from stactools.core.projection import reproject_geom
from stactools.sentinel1_grd.safe_manifest import SafeManifest
from stactools.sentinel1_grd.product_metadata import ProductMetadata
from stactools.sentinel1_grd.granule_metadata import GranuleMetadata

from tests import test_data


class Sentinel2MetadataTest(unittest.TestCase):
    def test_parses_product_metadata_properties(self):
        manifest_path = test_data.get_path(
            "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE"
        )

        manifest = SafeManifest(manifest_path)

        # Make a dict of the manifest
        manifest_dict = {
            "annotation_hrefs": manifest.annotation_hrefs,
            "calibration_hrefs": manifest.calibration_hrefs,
            "granule_href": manifest.granule_href,
            "href": manifest.href,
            "noise_hrefs": manifest.noise_hrefs,
            "thumbnail_href": manifest.thumbnail_href,
        }

        product_metadata = ProductMetadata(manifest.product_metadata_href)

        s1_props = product_metadata.metadata_dict
        s2_props.update(manifest_dict)

        expected = {
            # From product metadata
            "s1:product_uri": "S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8",
            "s1:instrument_configuration_ID": "7",
            "s1:product_type": "GRD",
            "s1:instrument_mode": "IW",
            "s1:datatake_id": "302867",
            "s1:polarisation": ["VV", "VH"],
            # From manifest metadata
            "annotation_hrefs": [
                "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE/annotation/s1a-iw-grd-vv-20210809t173953-20210809t174018-039156-049f13-001.xml",
                "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE/annotation/s1a-iw-grd-vh-20210809t173953-20210809t174018-039156-049f13-002.xml",
            ],
            "calibration_hrefs": [
                "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE/annotation/calibration/calibration-s1a-iw-grd-vh-20210809t173953-20210809t174018-039156-049f13-002.xml",
                "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE/annotation/calibration/calibration-s1a-iw-grd-vv-20210809t173953-20210809t174018-039156-049f13-001.xml",
            ],
            "granule_href": "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE",
            "href": "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE/manifest.safe",
            "noise_hrefs": [
                "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE/annotation/calibration/noise-s1a-iw-grd-vh-20210809t173953-20210809t174018-039156-049f13-002.xml",
                "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE/annotation/calibration/noise-s1a-iw-grd-vv-20210809t173953-20210809t174018-039156-049f13-001.xml",
            ],
            "thumbnail_href": "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE/preview/quick-look.png",
        }

        for k, v in expected.items():
            self.assertIn(k, s1_props)
            self.assertEqual(s1_props[k], v)
