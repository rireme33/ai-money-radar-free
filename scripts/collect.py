"""Free RSS collector. Candidates are not verified business opportunities."""
import hashlib
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data' / 'leads.json'
FEEDS = ['https://hnrss.org/show', 'https://news.ycombinator.com/rss']
AI = re.compile(r'\b(ai|llm|gpt|chatgpt|claude|agents?|automat\w*|mcp|coding)\b', re.I)
BUSINESS = re.compile(r'\b(saas|business|startup|revenue|profit|customers?|paid|product|app|tool|workflow|selling|sales|launch\w*)\b', re.I)
ATOM = '{http://www.w3.org/2005/Atom}'

def clean(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', value or ''))).strip()

def canonical(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/'), '', ''))

def parse_feed(contents):
    root = ET.fromstring(contents)
    entries = root.findall('.//item') or root.findall(ATOM + 'entry')
    for entry in entries:
        title = clean(entry.findtext('title') or entry.findtext(ATOM + 'title'))
        link = entry.findtext('link') or ''
        if not link:
            link_el = entry.find(ATOM + 'link')
            link = link_el.attrib.get('href', '') if link_el is not None else ''
        summary = clean(entry.findtext('description') or entry.findtext(ATOM + 'summary'))
        if title and urlsplit(link).scheme in ('http','https'):
            yield {'title': title, 'source_url': link, 'summary': summary[:280]}

def select(rows, previous):
    known = {canonical(x['source_url']) for x in previous}
    result = previous[:]
    for row in rows:
        text = row['title'] + ' ' + row['summary']
        url = canonical(row['source_url'])
        if not AI.search(text) or not BUSINESS.search(text) or url in known:
            continue
        known.add(url)
        result.append({'id': hashlib.sha256(url.encode()).hexdigest()[:16], **row,
                       'added_utc': datetime.now(timezone.utc).isoformat(),
                       'revenue_verified': False,
                       'note': '収益情報・商品としての需要は未検証'})
    return result[-300:]

def main():
    prior = json.loads(OUTPUT.read_text('utf-8')) if OUTPUT.exists() else []
    collected = []
    success = 0
    for feed in FEEDS:
        try:
            request = urllib.request.Request(feed, headers={'User-Agent': 'FreeAIRadar/1.0 (+manual RSS reader)'})
            with urllib.request.urlopen(request, timeout=18) as response:
                collected += list(parse_feed(response.read()))
            success += 1
        except Exception as exc:
            print(f'Feed error {feed}: {type(exc).__name__}', file=sys.stderr)
    if not success:
        print('All feeds failed; retaining previous output', file=sys.stderr)
        return 1
    updated = select(collected, prior)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + '\n', 'utf-8')
    print(f'Feed successes={success}/{len(FEEDS)}, saved={len(updated)}, new={len(updated)-len(prior)}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
