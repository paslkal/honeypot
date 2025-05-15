# Honeypot for Redis

Чтобы запустить лавушку, сначала нужно создать `.env` файл
```.env
REDIS_PASSWORD=passwd
REDIS_USER=my_user
REDIS_USER_PASSWORD=passwd
```

Затем запустить в терминале эти команды
```sh
docker-compose up
python3 main.py
```
Чтобы протестировать ловушку, введите в консоли `py honeypot_simulator.py`. <br/> 
Можно ввести любую команду, например `GET somekey`, `SET somekey somevalue` и т.д.