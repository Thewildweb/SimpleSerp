import csv
import base64
from typing import Optional


class UuleGenerator:
    def __init__(self):
        self._geo_dict = self._create_city_geos()

    def _create_city_geos(self, geo_path):
        len_nr_dict = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789- ABCDEFGHIJKLMOPQRSTUVWXYZ"
        with open(geo_path, "r") as geo_file:
            geo_dict = {}
            reader = csv.DictReader(geo_file)
            for row in reader:
                try:
                    loc_bytes = row["Canonical Name"].encode("ascii")
                except UnicodeEncodeError:
                    continue
                base64_loc = base64.b64encode(loc_bytes)
                try:
                    key = len_nr_dict[len(row["Canonical Name"])]
                except IndexError:
                    continue
                uule = "&uule=w+CAIQICI" + key + base64_loc.decode("UTF-8")
                country_code = row["Country Code"]

                geo_dict[row["Canonical Name"].lower()] = {
                    "uule": uule,
                    "cc": country_code,
                }

        return geo_dict

    def find_uule(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
    ):
        checklist = [i for i in [city, state, country] if i]
        for key, value in self._geo_dict.items():
            if all([i.lower() in key for i in checklist]):
                return value.get("uule")
