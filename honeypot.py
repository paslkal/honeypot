import socket
from db import execute_redis_command
import threading
from utils import plain_or_base64
from logger import Logger


class Honeypot:
    def __init__(self):
        self.bind_ip = "0.0.0.0"
        self.ports = [6379, 6380]  # Default ports to monitor

    def handle_connection(
        self,
        client_socket: socket.socket,
    ):
        """Handle individual connections and emulate services"""
        local_ip, local_port = client_socket.getsockname()
        remote_ip, remote_port = client_socket.getpeername()

        logger = Logger(
            local_ip=local_ip,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
        )

        logger.log_connection()

        try:
            # Receive data from attacker
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                query = data.decode()

                parts = query.split()
                command = parts[0].upper()
                if command == "QUIT":
                    response = execute_redis_command(query)
                    client_socket.send(response.encode())
                    logger.log_disconnection()
                    break

                if command == "AUTH":
                    username = "default"
                    password = ""
                    response = execute_redis_command(query)
                    if response == "OK":
                        auth_status = True
                    else:
                        auth_status = False
                    if len(parts) == 2:
                        password = parts[1]
                        response = execute_redis_command(query)
                    elif len(parts) == 3:
                        username, password = parts[1:]

                    logger.log_auth(
                        username=username,
                        password=password,
                        auth_status=auth_status,
                    )
                else:
                    response = execute_redis_command(query)
                    logger.log_command(
                        command_input=query,
                        command_output=response,
                        command_input_codec=plain_or_base64(query),
                        command_output_codec=plain_or_base64(response),
                    )
                # Send fake response
                client_socket.send(response.encode())
        except ConnectionResetError as e:
            logger.log_disconnection()

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
                    args=(client,),
                )
                client_handler.start()

        except Exception as e:
            print(f"Error starting listener on port {port}: {e}")
