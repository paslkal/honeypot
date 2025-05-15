import socket
import time

def main():
    ports = [6378, 6381]
    for port in ports:
        try:
            # Создаем и настраиваем сокет
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            # Подключаемся к серверу
            sock.connect(("0.0.0.0", port))
            # Получаем баннер   
            banner = sock.recv(1024)
            print(banner.decode())
            
            while True:
                command = input()
                if not command:
                    continue
                # Отправляем команду
                sock.send(command.encode())
                time.sleep(1)
                # Получаем ответ
                response = sock.recv(1024)
                print(response.decode())
            
        except socket.timeout:
            print("Error: Connection timed out")
        except ConnectionRefusedError:
            print("Error: Connection refused - check if Redis is running")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            sock.close()  # Всегда закрываем соединение

if __name__ == "__main__":
    main()
