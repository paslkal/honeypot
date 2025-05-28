import logging
import datetime
from pathlib import Path

# Configure logging directory
LOG_DIR = Path("honeypot_logs")
LOG_DIR.mkdir(exist_ok=True)


class Logger:
    def __init__(
        self, *, local_ip: str, remote_ip: str, local_port: int, remote_port: int
    ) -> None:
        # Creating a logger and setting handlers
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        log_file = (
            LOG_DIR / f"honeypot_{datetime.datetime.now().strftime('%Y%m%d')}.ndjson"
        )
        file_handler = logging.FileHandler(log_file)
        self.logger.addHandler(file_handler)

        self.local_ip = local_ip
        self.remote_ip = remote_ip
        self.local_port = local_port
        self.remote_port = remote_port

    def create_activity(self, event_id: str) -> dict[str, str | int]:
        activity = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "dest_ip": self.local_ip,
            "scr_ip": self.remote_ip,
            "dest_port": self.local_port,
            "src_port": self.remote_port,
            "protocol": "tcp",
            "event_id": event_id,
            "type": "cowrie",
        }

        return activity

    def log_connection(self):
        activity = self.create_activity("connection")

        self.logger.info(activity)

    def log_command(
        self,
        command_input: str,
        command_output: str,
        command_input_codec: str,
        command_output_codec: str,
    ):
        activity = self.create_activity("command_accept")

        activity["command_accept"] = {
            "command_input": command_input,
            "command_output": command_output,
            "command_input_codec": command_input_codec,
            "command_output_codec": command_output_codec,
        }

        self.logger.info(activity)

    def log_auth(
        self,
        username: str,
        password: str,
        auth_status: bool,
    ):
        activity = self.create_activity("authorization")

        activity["authorization"] = {
            "username": username,
            "password": password,
            "auth_status": auth_status,
        }

        self.logger.info(activity)

    def log_disconnection(self):
        activity = self.create_activity("disconnection")

        self.logger.info(activity)
