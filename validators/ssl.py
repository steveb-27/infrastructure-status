import os
from app.validator import Validator
from app.run_command import RunCommand
from datetime import datetime, timezone
from dotenv import load_dotenv


class SSLValidator(RunCommand,Validator):

    name = "SSL"

    def __init__(self):
        load_dotenv()
        self._server_config = os.getenv("CERTBOT_SERVER", "WEB_SERVER")

        self._host = os.getenv(self._server_config + "_HOST")
        self._port = int(os.getenv(self._server_config + "_PORT", "22"))
        self._user = os.getenv(self._server_config + "_USER")
        self._password = os.getenv(self._server_config + "_PASSWORD")

        if not self._host:
            raise RuntimeError(self._server_config + "_HOST is not configured.")

        if not self._user:
            raise RuntimeError(self._server_config + "_USER is not configured.")

        if not self._password:
            raise RuntimeError(self._server_config + "_PASSWORD is not configured.")

    def validate(self, context):
        _timestamp = datetime.now(timezone.utc)
        for cert in context.certificates:
            # Test if host is registered
            # TODO: Make test

            # Test if expired certificate
            value_exp = _timestamp
            value_fnd = cert['Expiry Date']
            context.add_result(
                validator=self.name + '|CERT-EXPIRED',
                config=cert['Certificate Name'],
                value_exp=value_exp,
                value_fnd=value_fnd,
                passes=value_fnd > value_exp
            )

