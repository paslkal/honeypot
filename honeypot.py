import socket
from pathlib import Path
import datetime
from db import execute_redis_command
import threading
import logging

# Configure logging directory
LOG_DIR = Path("honeypot_logs")
LOG_DIR.mkdir(exist_ok=True)


class Honeypot:
    def __init__(self, bind_ip="0.0.0.0", ports=None):
        self.bind_ip = bind_ip
        self.ports = ports or [6381, 6378, 6377]  # Default ports to monitor

        # Creating a logger and setting handlers
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        log_file = (
            LOG_DIR / f"honeypot_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        )
        file_handler = logging.FileHandler(log_file)
        self.logger.addHandler(file_handler)

    def log_activity(
        self,
        command_input: str | None = None,
        command_output: str | None = None,
        command_input_codec: str | None = None,
        command_output_codec: str | None = None,
        *,
        dest_ip: str,
        src_ip: str,
        dest_port: str,
        src_port: str,
        event_id: str,
    ):
        """Log suspicious activity with timestamp and details"""
        activity = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "dest_ip": dest_ip,
            "scr_ip": src_ip,
            "dest_port": dest_port,
            "src_port": src_port,
            "protocol": "tcp",
            "event_id": event_id,
            "type": "cowrie",
        }

        if event_id == "command_accept":
            activity["command_accept"] = {
                "command_input": command_input,
                "command_output": command_output,
                "command_input_codec": command_input_codec,
                "command_output_codec": command_output_codec,
            }

        self.logger.info(activity)

    def handle_connection(
        self,
        client_socket: socket.socket,
    ):
        """Handle individual connections and emulate services"""
        local_ip, local_port = client_socket.getsockname()
        remote_ip, remote_port = client_socket.getpeername()

        self.log_activity(
            dest_ip=local_ip,
            src_ip=remote_ip,
            dest_port=local_port,
            src_port=remote_port,
            event_id="authorization",
        )

        try:
            banner = f""""
                                _._                                                  
                        _.-``__ ''-._                                             
                    _.-``    `.  `_.  ''-._           Redis Open Source            
                .-`` .-```.  ```\/    _.,_ ''-._                                  
                (    '      ,       .-`  | `,    )     Running in standalone mode
                |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
                |    `-._   `._    /     _.-'    |     PID: 17
                `-._    `-._  `-./  _.-'    _.-'                                   
                |`-._`-._    `-.__.-'    _.-'_.-'|                                  
                |    `-._`-._        _.-'_.-'    |           https://redis.io       
                `-._    `-._`-.__.-'_.-'    _.-'                                   
                |`-._`-._    `-.__.-'    _.-'_.-'|                                  
                |    `-._`-._        _.-'_.-'    |                                  
                `-._    `-._`-.__.-'_.-'    _.-'                                   
                    `-._    `-.__.-'    _.-'                                       
                        `-._        _.-'                                           
                            `-.__.-'      
                {local_ip}:{local_port}>\n                      
            """

            # Send appropriate banner for the service
            client_socket.send(banner.encode())

            # Receive data from attacker
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                # Send fake response
                response = execute_redis_command(data) + f"\n{local_ip}:{local_port}> "
                #TODO: сделать функцию, которая будет различать кодировку: plain or base64
                self.log_activity(
                    dest_ip=local_ip,
                    src_ip=remote_ip,
                    dest_port=local_port,
                    src_port=remote_ip,
                    event_id="command_accept",
                    command_input=data.decode(),
                    command_output=response,
                    command_input_codec="plain",
                    command_output_codec="plain",
                )
                client_socket.send(response.encode())
        except ConnectionResetError as e:
            #TODO: сделать лог для disconnection
            print(f"Error handling connection: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
        finally:
            client_socket.close()

    def start_listener(self, port: int):
        """Start a listener on specified port"""
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.bind_ip, port))
            server.listen(5)

            print(f"[*] Listening on {self.bind_ip}:{port}")

            while True:
                client, addr = server.accept()
                print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

                # Handle connection in separate thread
                client_handler = threading.Thread(
                    target=self.handle_connection,
                    args=(client, ),
                )
                client_handler.start()

        except Exception as e:
            print(f"Error starting listener on port {port}: {e}")
