
def get_next(value: str) -> str:
    """Return next integer or alphabet character."""
    if len(value) == 1 and value.isalpha():
        return chr(ord(value) + 1 - 26 * (value in 'zZ'))

    if value.isdigit():
        return str(int(value) + 1)

    raise ValueError(f"Invalid: '{value}'")
