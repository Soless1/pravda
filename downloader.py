import requests
import random
import re
import uuid
import os
import fitz

from bs4 import BeautifulSoup
from urllib.parse import unquote
from datetime import datetime

BASE = "https://marxism-leninism.info"

YEAR_CACHE = None
ISSUE_CACHE = {}


# -------------------- CACHE --------------------

def get_year_pages():
    global YEAR_CACHE

    if YEAR_CACHE is not None:
        return YEAR_CACHE

    url = f"{BASE}/paper/pravda-1"
    html = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    YEAR_CACHE = list({
        BASE + a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].startswith("/paper/pravda_") and "-" in a["href"]
    })

    return YEAR_CACHE


def get_issues(year_url):
    global ISSUE_CACHE

    if year_url in ISSUE_CACHE:
        return ISSUE_CACHE[year_url]

    html = requests.get(year_url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    issues = list({
        BASE + a["href"] if a["href"].startswith("/") else a["href"]
        for a in soup.find_all("a", href=True)
        if "/paper/pravda_" in a["href"] and "_" in a["href"]
    })

    ISSUE_CACHE[year_url] = issues
    return issues


# -------------------- PARSING --------------------

def extract_pdf(issue_url):
    html = requests.get(issue_url).text

    pdf = re.search(r"https://[^\"']+\.pdf", html)
    if pdf:
        return pdf.group(0)

    file = re.search(r"file=([^\"']+)", html)
    if file:
        return unquote(file.group(1))

    selcdn = re.search(r"https://[^\"']+selcdn[^\"']+", html)
    if selcdn and ".pdf" in selcdn.group(0):
        return selcdn.group(0)

    return None


def download_pdf(url):
    filename = f"{uuid.uuid4().hex}.pdf"
    path = os.path.join("data/pdf", filename)

    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(1024 * 64):
            f.write(chunk)

    return path


def has_text_layer(pdf_path, min_chars=200):
    doc = fitz.open(pdf_path)

    total = sum(len(page.get_text().strip()) for page in doc)
    return total >= min_chars


# -------------------- GAME LOGIC --------------------

def get_today_issue_number():
    return datetime.now().timetuple().tm_yday


def find_today_issue(issues):
    today = get_today_issue_number()

    return [
        u for u in issues
        if (m := re.search(r"_(\d+)$", u)) and int(m.group(1)) == today
    ]


def run(max_attempts=10):
    print("🔎 Ищу выпуск газеты...")

    years = get_year_pages()
    if not years:
        return None, None

    today_issue = get_today_issue_number()

    for _ in range(max_attempts):

        year_url = random.choice(years)
        year = re.search(r"pravda_(\d{4})", year_url)
        year = year.group(1) if year else "unknown"

        issues = get_issues(year_url)
        if not issues:
            continue

        matching = find_today_issue(issues)
        issue = random.choice(matching) if matching else random.choice(issues)

        pdf_url = extract_pdf(issue)
        if not pdf_url:
            continue

        print("нашел пдф")
        pdf_path = download_pdf(pdf_url)
        print("скачал пдф, проверяю текстовый слой...")

        if has_text_layer(pdf_path):
            return pdf_path, year

    return None, None