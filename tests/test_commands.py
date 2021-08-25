import os
import pystac
from stactools.testing import CliTestCase
from pystac.utils import is_absolute_href
from tests import test_data
from tempfile import TemporaryDirectory
from pystac.extensions.eo import EOExtension
import sys

sys.path.append("/home/mlamare/repos/stac/sentinel1-grd/src")
from stactools.sentinel1_grd.constants import SENTINEL_POLARISATIONS
from stactools.sentinel1_grd.commands import create_sentinel1grd_command


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_sentinel1grd_command]

    def test_create_item(self):
        item_id = "S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8"
        granule_href = test_data.get_path(
            "data-files/S1A_IW_GRDH_1SDV_20210809T173953_20210809T174018_039156_049F13_6FF8.SAFE"
        )

        with self.subTest(granule_href):
            with TemporaryDirectory() as tmp_dir:
                cmd = ["sentinel1grd", "create-item", granule_href, tmp_dir]
                self.run_command(cmd)

                jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
                self.assertEqual(len(jsons), 1)
                fname = jsons[0]

                item = pystac.Item.from_file(os.path.join(tmp_dir, fname))

                # item.validate()

                self.assertEqual(item.id, item_id)

                bands_seen = set()

                for _, asset in item.assets.items():
                    # Ensure that there's no relative path parts
                    # in the asset HREFs
                    self.assertTrue("/./" not in asset.href)

                    self.assertTrue(is_absolute_href(asset.href))
                    asset_eo = EOExtension.ext(asset)
                    bands = asset_eo.bands
                    if bands is not None:
                        bands_seen |= set(b.name for b in bands)

                [
                    self.assertTrue(
                        x.lower() in list(SENTINEL_POLARISATIONS.keys()))
                    for x in bands_seen
                ]
