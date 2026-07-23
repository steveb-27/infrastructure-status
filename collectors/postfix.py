import os

import paramiko
from dotenv import load_dotenv

from collector import Collector


class PostfixCollector(Collector):

    name = "Postfix"

    def __init__(self):
        load_dotenv()

        self._host = os.getenv("MAIL_SERVER_HOST")
        self._port = int(os.getenv("MAIL_SERVER_PORT", "22"))
        self._user = os.getenv("MAIL_SERVER_USER")
        self._password = os.getenv("MAIL_SERVER_PASSWORD")

        if not self._host:
            raise RuntimeError("MAIL_SERVER_HOST is not configured.")

        if not self._user:
            raise RuntimeError("MAIL_SERVER_USER is not configured.")

        if not self._password:
            raise RuntimeError("MAIL_SERVER_PASSWORD is not configured.")

    def collect(self, context):
        client = self._connect()

        try:
            output = self._run_command(client, "postconf -n")
            output_parsed = self._parse(output)

            context.smtp_hostname = output_parsed.get('myhostname','')
            context.postfix = output_parsed

            print(f"Retrieved {len(context.postfix)} Postfix settings")

        finally:
            client.close()

    def _connect(self):
        client = paramiko.SSHClient()

        client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy()
        )

        client.connect(
            hostname=self._host,
            port=self._port,
            username=self._user,
            password=self._password,
            timeout=30,
        )

        return client

    def _run_command(self, client, command):
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode()
        error = stderr.read().decode()

        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            raise RuntimeError(error.strip())

        if error.strip():
            print(f"Warning: {error.strip()}")

        return output

    def _parse(self, output):
        config = {}

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            config[key.strip()] = value.strip()

        return config