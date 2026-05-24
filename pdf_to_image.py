import random
import uuid
import fitz


def pdf_to_image(pdf_path):
    doc = fitz.open(pdf_path)
    page = random.choice(list(doc)[1:])

    rect = page.rect

    # случайное окошко
    x0 = rect.width * random.uniform(0.05, 0.15)
    y0 = rect.height * random.uniform(0.15, 0.25)
    x1 = rect.width * random.uniform(0.85, 0.95)
    y1 = rect.height * random.uniform(0.75, 0.9)

    crop = fitz.Rect(x0, y0, x1, y1)

    pix = page.get_pixmap(clip=crop, dpi=120)

    path = f"data/{uuid.uuid4().hex}.png"
    pix.save(path)

    return path

# def pdf_to_image(pdf_path):
#     doc = fitz.open(pdf_path)
#     # page = random.choice(list(doc)[1:])
#     page = random.choice(list(doc)[0:1])
#
#     rect = page.rect
#
#     # случайное окошко
#     # x0 = rect.width * random.uniform(0.05, 0.15)
#     # y0 = rect.height * random.uniform(0.15, 0.25)
#     # x1 = rect.width * random.uniform(0.85, 0.95)
#     # y1 = rect.height * random.uniform(0.75, 0.9)
#     #
#     # crop = fitz.Rect(x0, y0, x1, y1)
#
#     # pix = page.get_pixmap(clip=crop, dpi=120)
#     pix = page.get_pixmap(dpi=120)
#
#     path = f"data/{uuid.uuid4().hex}.png"
#     pix.save(path)
#
#     return path