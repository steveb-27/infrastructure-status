import os

import requests
from dotenv import load_dotenv
from urllib.parse import urlparse
from collector import Collector


class BunnyCdnCollector(Collector):

    name = "Bunny CDN"

    def __init__(self):
        load_dotenv()

        token = os.getenv("BUNNYCDN_API_KEY")

        if not token:
            raise RuntimeError(
                "BUNNYCDN_API_KEY is not configured."
            )

        self._api = "https://api.bunny.net"

        self._headers = {
            "AccessKey": f"{token}",
        }

    def collect(self, context):
        zones = self._get_zones()

        print(f"Retrieved {len(zones)} zones")
        cdn = list()
        for zone in zones:
            if not zone['Enabled']:
                continue
            host_config = {
                'origin': urlparse(zone['OriginUrl']).netloc,
                'cdn': '',
                'hosts': list(),
            }
            for hostname in zone['Hostnames']:
                if hostname['IsSystemHostname']:
                    host_config['cdn'] = hostname['Value']
                else:
                    host_config['hosts'].append(hostname['Value'])
            cdn.append(host_config)

        context.bunnycdn_pull_zone = cdn

    def remediate(self, context):
        pass

    def _get_zones(self):
        response = requests.get(
            f"{self._api}/pullzone",
            headers=self._headers,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not response.status_code == 200:
            raise RuntimeError(
                "Bunny CDN API returned an error retrieving zones."
            )

        return data