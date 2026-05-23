import fitz
import re

import fitz


def extract_headlines(pdf_path):
    doc = fitz.open(pdf_path)

    headlines = []

    for page in doc:
        blocks = page.get_text("blocks")

        # сортируем как человек читает: сверху вниз, слева направо
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))

        for x0, y0, x1, y1, text, *_ in blocks:
            text = text.strip()

            if not text:
                continue

            # фильтр мусора
            if len(text) < 10 or len(text) > 120:
                continue

            # часто заголовки в газетах КАПСОМ
            if text.upper() != text:
                continue

            # убираем явный мусор
            if any(char.isdigit() for char in text) and len(text) < 30:
                continue

            headlines.append(text)

    # убираем дубликаты
    seen = set()
    result = []

    for h in headlines:
        if h not in seen:
            seen.add(h)
            result.append(h)

    return result[:25]