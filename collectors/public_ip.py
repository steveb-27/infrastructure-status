import requests
from app.collector import Collector


class PublicIpCollector(Collector):

    name = "Public IP"

    def __init__(self):
        self._url = "https://api.ipify.org?format=json"

    def collect(self, context):
        context.public_ip = self._get_public_ip()

        print(f"Public IP: {context.public_ip}")

    def remediate(self, context):
        pass

    def _get_public_ip(self):
        response = requests.get(
            self._url,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data.get('ip',False)