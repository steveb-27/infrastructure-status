import subprocess
import paramiko


class RunCommand:
    def run_command(self, command):
        """Connect to a terminal, local or ssh"""
        if self._host.lower() == 'local':
            return self._run_local_command(command)
        else:
            return self._run_remote_command(command)

    def _run_local_command(self, command):
        """Run command locally"""
        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        return result.stdout + result.stderr

    def _run_remote_command(self, command):
        """Run command over SSH"""
        client = self._connect()
        try:
            stdin, stdout, stderr = client.exec_command(command)

            output = stdout.read().decode()
            error = stderr.read().decode()

            exit_status = stdout.channel.recv_exit_status()
        finally:
            client.close()

        if exit_status != 0:
            raise RuntimeError(error.strip())

        return output + error

    def _connect(self):
        """Establish SSH connection"""
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

