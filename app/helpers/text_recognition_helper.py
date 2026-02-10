import re

def reorder_numbered_text(s: str) -> str:
    """
    Reorders numbered text blocks if numbering is continuous from 1..N.
    Otherwise returns the original string.
    """

    # Match: number + optional whitespace + text (lazy) until next number or end
    pattern = re.compile(
        r'(?m)(\d+)\s*(.*?)(?=\n?\d+\s*|\Z)',
        re.DOTALL
    )

    matches = pattern.findall(s)

    if not matches:
        return s

    blocks = {}
    numbers = []

    for num_str, text in matches:
        num = int(num_str)
        numbers.append(num)

        # normalize text a bit
        blocks[num] = text.strip()

    # Check numbering validity
    numbers_sorted = sorted(numbers)

    # Must start at 1 and be continuous
    if numbers_sorted[0] != 1:
        return s

    for i in range(1, len(numbers_sorted)):
        if numbers_sorted[i] != numbers_sorted[i - 1] + 1:
            return s

    # Rebuild output
    ordered_parts = []
    for n in range(1, numbers_sorted[-1] + 1):
        ordered_parts.append(f"{n} {blocks[n]}")

    return "\n\n".join(ordered_parts)
