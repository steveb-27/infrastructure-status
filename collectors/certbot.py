import os

from dotenv import load_dotenv
from datetime import datetime
from app.collector import Collector
from app.run_command import RunCommand

class Certbot(RunCommand,Collector):

    name = "Certbot"

    def __init__(self):
        load_dotenv()
        self._server_config = os.getenv("CERTBOT_SERVER", "WEB_SERVER")

        self._password = os.getenv(self._server_config + "_PASSWORD")
        self._host = os.getenv(self._server_config + "_HOST")
        self._port = int(os.getenv(self._server_config + "_PORT", "22"))
        self._user = os.getenv(self._server_config + "_USER")

        if not self._host:
            raise RuntimeError(self._server_config + "_HOST is not configured.")

        if not self._user:
            raise RuntimeError(self._server_config + "_USER is not configured.")

        if not self._password:
            raise RuntimeError(self._server_config + "_PASSWORD is not configured.")

    def collect(self, context):
        command = f"certbot certificates"
        output = self.sudo_command(command)

        self._parse(output, context)

        print(
            f"Retrieved {len(context.certificates)} certbot certificates"
        )

    def remediate(self, context):
        _certbot_errors = [
            found_error
            for found_error in context.results if found_error['validator'].split('|', 1)[0] == 'CERTBOT'
        ]

        _ssl_errors = [
            found_error
            for found_error in context.results if found_error['validator'].split('|', 1)[0] == 'SSL'
        ]

    def _parse(self,output, context):
        """Parse output from 'certbot certificates' command"""
        certificates = []
        given_errors = []

        for line in output.splitlines():
            if line[:3] == '- -':
                # Skip design element at beginning and end of response
                continue
            elif 'Found the following certs' in line:
                # Beginning of the list of certificates
                errors = False
                certs = True
                certificate = dict()
                continue
            elif line[:4] == '    ':
                # Rows of certificate info that follow the certificate name
                if certs:
                    fields = line[4:].split(': ',1)
                    if fields[0] == 'Expiry Date':
                        clean_timestamp = fields[1].split(" (")[0]
                        field_value = datetime.fromisoformat(clean_timestamp)
                    elif fields[0] == 'Identifiers':
                        field_value = fields[1].split(' ')
                    else:
                        field_value = fields[1]
                    certificate[fields[0]] = field_value
            elif line[:2] == '  ':
                # First row of certificate data with the certificate name
                if certs:
                    # Every new beginning comes from some other beginning's end
                    if len(certificate) > 0:
                        certificates.append(certificate.copy())
                        certificate.clear()
                    fields = line[2:].split(': ',1)
                    certificate[fields[0]] = fields[1]
                if errors:
                    given_errors.append(line.strip())
            elif 'The following renewal configurations were invalid' in line:
                if len(certificate) > 0:
                    certificates.append(certificate)
                errors = True
                certs = False
        context.certificates = certificates

        #
        # Self Contained Tests
        #

        # The command volunteers configuration errors, pass these directly as results without validation
        for error in given_errors:
            context.add_result(
                validator='CERTBOT|CONF-ERRROR',
                config="Renewal configuration invalid",
                value_exp='',
                value_fnd=error,
                passes=False
            )