import os, re
import subprocess

import paramiko
from dotenv import load_dotenv

from collector import Collector


class NginxCollector(Collector):

    name = "Nginx"

    SERVER_RE = re.compile(r"^server\s*\{$")
    SERVER_NAME_RE = re.compile(r"^server_name\s+(.+);$")
    CONFIG_RE = re.compile(r"^# configuration file (.+):$")

    def __init__(self):
        load_dotenv()

        self._mode = os.getenv("NGINX_MODE", "local").lower()
        self._password = os.getenv("WEB_SERVER_PASSWORD")

        if self._mode == "ssh":
            self._host = os.getenv("WEB_SERVER_HOST")
            self._port = int(os.getenv("WEB_SERVER_PORT", "22"))
            self._user = os.getenv("WEB_SERVER_USER")

            if not self._host:
                raise RuntimeError("WEB_SERVER_HOST is not configured.")

            if not self._user:
                raise RuntimeError("WEB_SERVER_USER is not configured.")

            if not self._password:
                raise RuntimeError("WEB_SERVER_PASSWORD is not configured.")

    def collect(self, context):
        configuration = self._get_configuration()

        context.nginx_sites = self._parse(configuration)

        print(
            f"Retrieved {len(context.nginx_sites)} nginx server block(s)"
        )

    def _get_configuration(self):
        command = f"echo '{self._password}' | sudo -S -p '' nginx -T"

        if self._mode == "local":
            return self._run_local_command(command)

        if self._mode == "ssh":
            client = self._connect()

            try:
                return self._run_remote_command(
                    client,
                    command
                )

            finally:
                client.close()

        raise RuntimeError(
            f"Unsupported NGINX_MODE: {self._mode}"
        )

    def _run_local_command(self, command):
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        return result.stdout + result.stderr

    def _connect(self):
        client = paramiko.SSHClient()

        client.load_system_host_keys()
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

    def _run_remote_command(self, client, command):
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode()
        error = stderr.read().decode()

        exit_status = stdout.channel.recv_exit_status()

        if exit_status != 0:
            raise RuntimeError(error.strip())

        return output + error

    def _parse(self, configuration):
        servers = []

        current_file = None
        current_server = None
        brace_depth = 0

        for line in configuration.splitlines():

            line = line.strip()

            if not line:
                continue

            # Configuration file marker
            if match := self.CONFIG_RE.match(line):
                current_file = match.group(1)
                continue

            # Skip comments
            if line.startswith('#'):
                continue

            # Enter server block
            if self.SERVER_RE.match(line) or line == 'server':
                current_server = {
                    "config": current_file,
                    "server_names": []
                }

                brace_depth = 1
                continue

            # Not inside a server block
            if current_server is None:
                continue

            # Track nesting
            brace_depth += line.count("{")
            brace_depth -= line.count("}")

            # server_name
            if match := self.SERVER_NAME_RE.match(line):
                current_server["server_names"].extend(
                    match.group(1).split()
                )

            # End of server block
            if brace_depth == 0:
                servers.append(current_server)
                current_server = None

        return servers