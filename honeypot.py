import socket
from pathlib import Path
import datetime
import json
from db import execute_redis_command
import threading

# Configure logging directory
LOG_DIR = Path("honeypot_logs")
LOG_DIR.mkdir(exist_ok=True)


class Honeypot:
    def __init__(self, bind_ip="0.0.0.0", ports=None):
        self.bind_ip = bind_ip
        self.ports = ports or [6381, 6378]  # Default ports to monitor
        self.active_connections = {}
        self.log_file = (
            LOG_DIR / f"honeypot_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        )

    def log_activity(
        self, *, dest_ip: str, src_ip: str, dest_port: str, src_port: str, event_id: str
    ):
        """Log suspicious activity with timestamp and details"""
        activity = {
            "dest_ip": dest_ip,
            "scr_ip": src_ip,
            "dest_port": dest_port,
            "src_port": src_port,
            "protocol": "tcp",
            "event_id": event_id,
            "type": "cowrie",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        with open(self.log_file, "a") as f:
            json.dump(activity, f)
            f.write("\n")

    def handle_connection(self, client_socket, dest_ip, dest_port, src_ip, src_port):
        """Handle individual connections and emulate services"""
        
        self.log_activity(
            dest_ip=dest_ip,
            src_ip=src_ip,
            dest_port=dest_port,
            src_port=src_port,
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
                {dest_ip}:{dest_port}>\n                      
            """

            # Send appropriate banner for the service
            client_socket.send(banner.encode())

            # Receive data from attacker
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                self.log_activity(
                    dest_ip=dest_ip,
                    src_ip=src_ip,
                    dest_port=dest_port,
                    src_port=src_port,
                    event_id="command_accept",
                )

                # Send fake response
                response = execute_redis_command(data) + f"\n{dest_ip}:{dest_port}>\n"
                client_socket.send(response.encode())
        except Exception as e:
            print(f"Error handling connection: {e}")
        finally:
            client_socket.close()

    def start_listener(self, port:str):
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
                    target=self.handle_connection, args=(client, "198.162.10.1", port, addr[0], addr[1])
                )
                client_handler.start()

        except Exception as e:
            print(f"Error starting listener on port {port}: {e}")
