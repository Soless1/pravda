import fitz


def extract_headlines(pdf_path, top_n=20):
    doc = fitz.open(pdf_path)

    candidates = []

    for page in doc:
        data = page.get_text("dict")

        for block in data["blocks"]:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                line_text = ""
                max_size = 0

                for span in line["spans"]:
                    text = span["text"].strip()
                    size = span["size"]

                    line_text += text + " "
                    max_size = max(max_size, size)

                line_text = line_text.strip()

                if not line_text:
                    continue

                candidates.append((line_text, max_size))

    # сортируем по размеру шрифта (главный сигнал)
    candidates.sort(key=lambda x: x[1], reverse=True)

    headlines = []
    seen = set()

    for text, size in candidates:
        text = text.strip()

        # фильтры мусора
        if len(text) < 6:
            continue

        if text.isdigit():
            continue

        if text in seen:
            continue

        seen.add(text)
        headlines.append(text)

        if len(headlines) >= top_n:
            break

    return headlines