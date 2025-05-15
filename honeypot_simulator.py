import socket
import time
from concurrent.futures import ThreadPoolExecutor

def test():
    try:
        # Создаем и настраиваем сокет
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        # Подключаемся к серверу
        sock.connect(("0.0.0.0", 6381))
        
        # Получаем баннер
        banner = sock.recv(1024)
        print("Banner:", banner.decode())
        
        # Отправляем команду
        sock.send(b'set k 100\n')  # Добавляем \n для Redis протокола
        time.sleep(1)
        # Получаем ответ
        response = sock.recv(1024)
        print("Response:", response.decode())
        
    except socket.timeout:
        print("Error: Connection timed out")
    except ConnectionRefusedError:
        print("Error: Connection refused - check if Redis is running")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        sock.close()  # Всегда закрываем соединение

if __name__ == "__main__":
    # main()
    test()
