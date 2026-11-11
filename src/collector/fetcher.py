import requests

USER_AGENT = "info-collector/0.1 (student project;contact:https://github.com/aismzl0/info-collector.git)"
TIMEOUT_SECONDS = 10


def fetch_page(url:str) -> str:
    headers = {"User-Agent":USER_AGENT}
    response = requests.get(url,headers=headers,timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.text

if __name__ == '__main__':
    from pathlib import Path


    html = fetch_page("https://news.ycombinator.com/")
    out = Path("tests/fixtures/hn_sample.html")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(html,encoding="utf-8")
    print(f"Saved{len(html)} characters to {out}")