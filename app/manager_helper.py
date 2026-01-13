
def get_next(value: str) -> str:
    """Return next integer or alphabet character."""
    if len(value) == 1 and value.isalpha():
        return chr(ord(value) + 1 - 26 * (value in 'zZ'))

    if value.isdigit():
        return str(int(value) + 1)

    raise ValueError(f"Invalid: '{value}'")

def check_repeat_id(id: str | int) -> tuple[bool, str | int]:
    if isinstance(id, int) and id > 999 and id % 1000 == 0:
        return True, int(id / 1000)
    if isinstance(id, str) and (id.endswith("+++")):
        return True, id.replace("+++", "")
    return False, id
