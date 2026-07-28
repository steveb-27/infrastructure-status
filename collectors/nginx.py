import os, re
from dotenv import load_dotenv

from collector import Collector


class NginxCollector(Collector):

    name = "Nginx"

    SERVER_RE = re.compile(r"^server\s*\{$")
    SERVER_NAME_RE = re.compile(r"^server_name\s+(.+);$")
    CONFIG_RE = re.compile(r"^# configuration file (.+):$")

    def __init__(self):
        load_dotenv()
        self._server_config = os.getenv("NGINX_SERVER", "WEB_SERVER")

        self._mode = os.getenv(self._server_config + "_HOST", "local").lower()
        self._password = os.getenv(self._server_config + "_PASSWORD")

        if self._mode != "local":
            self._mode = 'ssh'
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
        command = f"echo '{self._password}' | sudo -S -p '' nginx -T"
        output = self.run_command(command)

        context.nginx_sites = self._parse(output)

        print(
            f"Retrieved {len(context.nginx_sites)} nginx server block(s)"
        )

    def remediate(self, context):
        pass

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