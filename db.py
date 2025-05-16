import redis
from env import REDIS_USER_PASSWORD, REDIS_USER

r = redis.Redis(
    host="localhost",
    port=6360,
    username=REDIS_USER,
    password=REDIS_USER_PASSWORD,
    decode_responses=True,
    db=0,
)


def execute_redis_command(command: str) -> str:
    try:
        parts = command.split()
        if not parts:
            return ""

        cmd = parts[0].upper()
        args = parts[1:]

        if cmd == "GET":
            if len(args) != 1:
                return "(error) ERR wrong number of arguments for 'get' command"
            return r.get(args[0])
        elif cmd == "SET":
            if len(args) < 2:
                return "(error) ERR wrong number of arguments for 'set' command"
            return str(r.set(args[0], " ".join(args[1:])))
        else:
            return str(r.execute_command(*parts))

    except redis.RedisError as e:
        return f"Ошибка Redis: {e}"
    except Exception as e:
        return f"Общая ошибка: {e}"
