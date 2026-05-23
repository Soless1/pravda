import requests
import random
import re
import uuid
import fitz
from bs4 import BeautifulSoup
from urllib.parse import unquote

BASE = "https://marxism-leninism.info"


def get_year_pages():
    url = f"{BASE}/paper/pravda-1"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    years = []

    for a in soup.find_all("a"):
        href = a.get("href")

        if href and href.startswith("/paper/pravda_") and "-" in href:
            years.append(BASE + href)

    return list(set(years))


def get_issues(year_url):
    html = requests.get(year_url).text
    soup = BeautifulSoup(html, "html.parser")

    issues = []

    for a in soup.find_all("a"):
        href = a.get("href")

        if href and "/paper/pravda_" in href and "_" in href:
            if href.startswith("/"):
                href = BASE + href
            issues.append(href)

    return list(set(issues))


def extract_pdf(issue_url):
    html = requests.get(issue_url).text

    pdfs = re.findall(r"https://[^\"']+\.pdf", html)
    if pdfs:
        return pdfs[0]

    files = re.findall(r"file=([^\"']+)", html)
    if files:
        return unquote(files[0])

    data_urls = re.findall(r"https://[^\"']+selcdn[^\"']+", html)
    for u in data_urls:
        if ".pdf" in u:
            return u

    return None


def download_pdf(url):
    import uuid
    import os

    filename = f"{uuid.uuid4().hex}.pdf"
    path = os.path.join("data/pdf", filename)

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers, stream=True)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(1024 * 64):
            f.write(chunk)

    return path
def has_text_layer(pdf_path, min_chars=200):
    doc = fitz.open(pdf_path)
    total = 0

    for page in doc:
        total += len(page.get_text().strip())
        if total >= min_chars:
            return True

    return False


def run(max_attempts=10):
    years = get_year_pages()
    if not years:
        return None

    for _ in range(max_attempts):
        year = random.choice(years)

        issues = get_issues(year)
        if not issues:
            continue

        issue = random.choice(issues)

        pdf_url = extract_pdf(issue)
        if not pdf_url:
            continue

        file = download_pdf(pdf_url)

        if has_text_layer(file):
            return file

    return None