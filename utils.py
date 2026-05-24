import random

def generate_year_options(correct_year: int):
    options = {correct_year}

    while len(options) < 4:
        # делаем сильно отличающиеся годы
        offset = random.randint(10, 40)
        fake = correct_year + random.choice([-offset, offset])

        # ограничим разумный диапазон СССР/XX век
        if 1918 <= fake <= 1991:
            options.add(fake)

    options = list(options)
    random.shuffle(options)
    return options