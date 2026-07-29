import os
import requests
from dotenv import load_dotenv
from app.collector import Collector


class CloudflareDnsCollector(Collector):

    name = "Cloudflare DNS"

    def __init__(self):
        load_dotenv()

        token = os.getenv("CLOUDFLARE_API_TOKEN")

        if not token:
            raise RuntimeError(
                "CLOUDFLARE_API_TOKEN is not configured."
            )

        self._api = "https://api.cloudflare.com/client/v4"

        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def collect(self, context):
        zones = self._get_zones()

        print(f"Retrieved {len(zones)} zones")

        for zone in zones:
            zone["records"] = self._get_dns_records(
                zone["id"]
            )

        context.domains = zones

    def remediate(self, context):
        _dns_errors = [
            found_error
            for found_error in context.results
            if found_error['validator'].split('|', 1)[0] == 'DNS'
               and not 'CDN' in found_error['validator']
               and not 'NGINX' in found_error['validator']
        ]

    def _get_zones(self):
        response = requests.get(
            f"{self._api}/zones",
            headers=self._headers,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            raise RuntimeError(
                "Cloudflare API returned an error retrieving zones."
            )

        return data["result"]

    def _get_dns_records(self, zone_id):
        response = requests.get(
            f"{self._api}/zones/{zone_id}/dns_records",
            headers=self._headers,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            raise RuntimeError(
                "Cloudflare API returned an error retrieving DNS records."
            )

        return data["result"]