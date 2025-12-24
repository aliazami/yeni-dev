def get_first_missing_index(numbers):
    if not numbers:
        return None

    existing = set(numbers)
    max_val = max(numbers)

    # We only check up to max_val.
    # We don't need to check max_val itself because we know it exists!
    for i in range(1, max_val):
        if i not in existing:
            return i

    return None