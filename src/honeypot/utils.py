def is_likely_binary_or_encoded(string: str) -> bool:
    # Проверим: содержит ли строка escape-последовательности или не-ASCII символы
    try:
        bytes_value = bytes(string, "utf-8").decode("unicode_escape").encode("latin1")
        return any(c < 32 or c > 126 for c in bytes_value)
    except Exception:
        return True  # если что-то не так при преобразовании — подозреваем бинарность


def plain_or_base64(string: str) -> str:
    if is_likely_binary_or_encoded(string):
        return "base64"

    return "plain"
