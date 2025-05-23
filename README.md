# Honeypot for Redis

Чтобы запустить ловушку, сначала нужно создать `.env` файл
```.env
REDIS_PASSWORD=passwd
REDIS_USER=my_user
REDIS_USER_PASSWORD=passwd
```

Затем запустить в терминале эти команды
```sh
docker-compose up --build
```
Чтобы протестировать ловушку, введите в консоли `python3 honeypot_simulator.py`. <br/> 
Можно ввести любую команду, например `GET somekey`, `SET somekey somevalue` и т.д.