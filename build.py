"""从词汇本生成无需网络即可打开的日期导航页面。"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def render(source):
    source = re.sub(r'<!--[\s\S]*?-->', '', source)
    days = []
    for line in source.splitlines():
        if re.fullmatch(r'## \d{4}-\d{2}-\d{2}', line):
            days.append({'date': line[3:], 'words': []})
        elif line.startswith('### ') and days:
            days[-1]['words'].append({'title': line[4:], 'fields': []})
        elif line.startswith('- **') and days and days[-1]['words']:
            match = re.fullmatch(r'- \*\*(.+?)\*\*：(.*)', line)
            if match:
                days[-1]['words'][-1]['fields'].append(match.groups())
    esc = html.escape
    nav, sections = [], []
    total = sum(len(day['words']) for day in days)
    for day in days:
        date, words = day['date'], day['words']
        nav.append(f'<a href="#day-{date}"><span>{date}</span><small>{len(words)} 词</small></a>')
        cards = []
        for word in words:
            fields = ''.join(f'<div class="field"><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>' for label, value in word['fields'])
            spoken = re.sub(r'^\d+\.\s*', '', word['title'])
            cards.append(f'<article><div class="word-heading"><h3 lang="en">{esc(word["title"])}</h3><button type="button" class="pronounce" data-word="{esc(spoken)}" aria-label="朗读 {esc(spoken)}">▶ 读音</button></div><dl>{fields}</dl></article>')
        sections.append(f'<section id="day-{date}" tabindex="-1"><header><h2>{date}</h2><span>{len(words)} 个词汇</span></header>{"".join(cards)}</section>')
    template = (ROOT / 'template.html').read_text(encoding='utf-8')
    return template.replace('{{NAV}}', ''.join(nav)).replace('{{CONTENT}}', ''.join(sections) or '<p>还没有词汇记录。</p>').replace('{{TOTAL}}', str(total)).replace('{{DAYS}}', str(len(days)))


if __name__ == '__main__':
    (ROOT / 'index.html').write_text(render((ROOT / '英语词汇本.md').read_text(encoding='utf-8')), encoding='utf-8')
    print('已更新 index.html')
