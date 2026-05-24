import os
import random
import re
import uuid
from datetime import datetime, timezone
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://marxism-leninism.info"

YEAR_CACHE = None
ISSUE_CACHE = {}

# ----------------------------
# HTTP session
# ----------------------------
session = requests.Session()

retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)

session.mount("https://", HTTPAdapter(max_retries=retry))

session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


def safe_get(url, timeout=15):
    try:
        return session.get(url, timeout=timeout)
    except requests.RequestException:
        return None


# ----------------------------
# Parsing
# ----------------------------
def get_year_pages():
    global YEAR_CACHE

    if YEAR_CACHE:
        return YEAR_CACHE

    url = f"{BASE}/paper/pravda-1"

    r = safe_get(url)
    if not r:
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    years = []

    for a in soup.find_all("a"):
        href = a.get("href")

        if href and href.startswith("/paper/pravda_") and "-" in href:
            years.append(BASE + href)

    YEAR_CACHE = list(set(years))

    return YEAR_CACHE


def get_issues(year_url):
    global ISSUE_CACHE

    if year_url in ISSUE_CACHE:
        return ISSUE_CACHE[year_url]

    r = safe_get(year_url)

    if not r:
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    issues = []

    for a in soup.find_all("a"):
        href = a.get("href")

        if href and "/paper/pravda_" in href and "_" in href:
            if href.startswith("/"):
                href = BASE + href

            issues.append(href)

    ISSUE_CACHE[year_url] = list(set(issues))

    return ISSUE_CACHE[year_url]


def extract_pdf(issue_url):
    r = safe_get(issue_url)

    if not r:
        return None

    html = r.text

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


# ----------------------------
# Download
# ----------------------------
def download_pdf(url):
    os.makedirs("data/pdf", exist_ok=True)

    filename = f"{uuid.uuid4().hex}.pdf"

    path = os.path.join("data/pdf", filename)

    r = safe_get(url, timeout=30)

    if not r:
        return None

    with open(path, "wb") as f:
        for chunk in r.iter_content(1024 * 64):
            f.write(chunk)

    return path


# ----------------------------
# Date logic
# ----------------------------
def get_today_issue_number():
    return datetime.now(timezone.utc).timetuple().tm_yday


def extract_issue_number(url):
    nums = re.findall(r"\d+", url)

    if len(nums) < 2:
        return None
    return int(nums[-2])


def find_today_issue(issues):
    today = get_today_issue_number()

    return [
        issue
        for issue in issues
        if extract_issue_number(issue) == today
    ]



# ----------------------------
# Main
# ----------------------------
def run(max_attempts=10):
    print("🔎 Ищу выпуск газеты...")

    years = get_year_pages()

    if not years:
        return None, None

    random.shuffle(years)

    attempts = 0

    for year_url in years:
        if attempts >= max_attempts:
            break

        attempts += 1

        match = re.search(r"pravda_(\d{4})", year_url)

        year = match.group(1) if match else "unknown"

        print(f"📅 Проверяю {year}")

        issues = get_issues(year_url)

        if not issues:
            continue

        today_issues = find_today_issue(issues)

        if today_issues:
            issue = random.choice(today_issues)
            print("✅ Нашел выпуск за сегодняшний день")
        else:
            print("⚠️ Нет выпуска за сегодняшний день")
            continue

        pdf_url = extract_pdf(issue)

        if not pdf_url:
            continue

        print("📄 Нашел PDF")

        pdf_path = download_pdf(pdf_url)

        if not pdf_path:
            continue

        print("⬇️ PDF скачан")

        return pdf_path, year

    return None, None

