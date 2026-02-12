import re
import itertools


def expand_text(text: str) -> list[str]:
    """
    Expands patterns like:
        I/he/she like(s) apple/orange.

    Rules:
        - words separated by "/" → exactly one must be chosen
        - text inside "(...)" → optional (present or removed)
    """

    # Step 1: Expand optional parentheses first
    def expand_parentheses(s: str):
        pattern = re.compile(r"\(([^()]+)\)")

        results = [s]
        while True:
            new_results = []
            expanded = False

            for item in results:
                match = pattern.search(item)
                if match:
                    expanded = True
                    content = match.group(1)

                    # without parentheses content
                    without = item[:match.start()] + item[match.end():]

                    # with parentheses content
                    with_ = item[:match.start()] + content + item[match.end():]

                    new_results.extend([without, with_])
                else:
                    new_results.append(item)

            results = new_results

            if not expanded:
                break

        return results

    # Step 2: Expand slash-separated alternatives
    def expand_slashes(s: str):
        tokens = s.split()

        options = []
        for token in tokens:
            # separate trailing punctuation like "." "," "!"
            m = re.match(r"^(.*?)([.,!?;:]*)$", token)
            core = m.group(1)
            punct = m.group(2)

            if "/" in core:
                parts = core.split("/")
                options.append([p + punct for p in parts])
            else:
                options.append([token])

        return [" ".join(combo) for combo in itertools.product(*options)]

    # Expand parentheses first
    stage1 = expand_parentheses(text)

    # Then expand slashes
    final_results = []
    for item in stage1:
        final_results.extend(expand_slashes(item))

    return final_results




def answer_expansion(original_answer: str):
    possible_answers = set()
    master_chunks = original_answer.split(" / ")
    for master_chunk in master_chunks:
        if "/" in master_chunk or "(" in master_chunk:
            minor_chunks = expand_text(master_chunk)
            possible_answers.update(minor_chunks)
        else:
            possible_answers.add(master_chunk)

    return possible_answers