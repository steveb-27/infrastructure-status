import os
from app.validator import Validator
from app.run_command import RunCommand
from datetime import datetime, timezone
from dotenv import load_dotenv


class EmailValidator(RunCommand,Validator):

    name = "SMTP"

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
        # Check for mapped relayhost
        value_exp = False
        value_fnd = context.postfix.get('sender_dependent_relayhost_maps',False)
        context.add_result(
            validator=self.name,
            config="sender_dependent_relayhost_mapse",
            value_exp = value_exp,
            value_fnd = value_fnd,
            passes = value_exp == value_fnd
        )

        # Check for single relayhost
        value_exp = False
        value_fnd = context.postfix.get('relayhost', False)
        context.add_result(
            validator=self.name,
            config="relayhost",
            value_exp=value_exp,
            value_fnd=value_fnd,
            passes=value_exp == value_fnd
        )

        # Check if smtp_tls_cert_file certificate is self-signed
        value_exp = 'REAL CERT'
        value_fnd = context.postfix_smtp_auth
        context.add_result(
            validator=self.name + '|CERT|AUTHORITY',
            config="smtp_tls_cert_file",
            value_exp=value_exp,
            value_fnd=value_fnd,
            passes=value_exp == value_fnd
        )

        # Check if smtpd_tls_cert_file certificate is self-signed
        value_exp = 'REAL CERT'
        value_fnd = context.postfix_smtpd_auth
        context.add_result(
            validator=self.name + '|CERT|AUTHORITY',
            config="smtpd_tls_cert_file",
            value_exp=value_exp,
            value_fnd=value_fnd,
            passes=value_exp == value_fnd
        )

        # Retrieve non-expired Certbot certificates that match the email server's configured hostname
        _timestamp = datetime.now(timezone.utc)
        context.postfix_valid_certs = [
            cert
            for cert in context.certificates
            if context.smtp_hostname in cert["Identifiers"] and cert['Expiry Date'] > _timestamp
        ]
        # Test if SMTP serial number is in valid host certificate list
        value_exp = [str(cert['Serial Number']) for cert in context.postfix_valid_certs]
        value_fnd = context.postfix_smtp_serial
        context.add_result(
            validator=self.name + '|CERT|SERIAL-MATCH',
            config="smtp_tls_cert_file",
            value_exp=value_exp,
            value_fnd=value_fnd,
            passes=value_fnd in value_exp
        )

        # Test if SMTPD serial number is in valid host certificate list
        value_exp = [cert['Serial Number'] for cert in context.postfix_valid_certs]
        value_fnd = context.postfix_smtpd_serial
        context.add_result(
            validator=self.name + '|CERT|SERIAL-MATCH',
            config="smtpd_tls_cert_file",
            value_exp=value_exp,
            value_fnd=value_fnd,
            passes=value_fnd in value_exp
        )