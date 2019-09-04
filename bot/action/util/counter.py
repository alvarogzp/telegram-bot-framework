import collections


def case_insensitive_counter(elements):
    counter = collections.Counter(elements)

    elements_lower = {}
    for element in counter:
        element_lower = element.lower()
        elements_lower.setdefault(element_lower, []).append(element)

    for _, cases in elements_lower.items():
        if len(cases) > 1:
            most_used_case = max(cases, key=lambda case: counter[case])
            total_occurrences = sum((counter[case] for case in cases))
            counter[most_used_case] = total_occurrences
            for case in cases:
                if case != most_used_case:
                    del counter[case]

    return counter
