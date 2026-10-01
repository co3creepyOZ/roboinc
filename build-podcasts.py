from pathlib import Path
import re, json, html, shutil, hashlib
from urllib.parse import quote
SITE = Path(__file__).resolve().parent
def esc(s): return html.escape(str(s), quote=True)
def url(s): return quote(str(s).replace(chr(92), '/'), safe='/')
def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8')

def sync_ready_podcasts():
    source = SITE.parent.parent
    transcripts = source/'scripts/Транскрипції'
    audio_root = source/'podcast'
    manifest = SITE/'podcasts/manifest.json'
    previous = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    if not transcripts.is_dir() or not audio_root.is_dir():
        # Standalone checkout: rebuild from the already synced release files.
        return
    existing = {r['id']: r for r in previous}
    ready = []
    pending = []
    for transcript in sorted(transcripts.glob('*.md')):
        match = re.fullmatch(r'([5-7]) клас — Урок ([0-9]+) — (.+)', transcript.stem)
        if not match:
            continue
        grade, number, title = int(match[1]), int(match[2]), match[3]
        text = transcript.read_text(encoding='utf-8-sig')
        audio_match = re.search(r'Аудіо: *' + chr(96) + r'([^' + chr(96) + r']+)' + chr(96), text)
        if not audio_match:
            pending.append(transcript.name + ': не вказано аудіофайл')
            continue
        audio = (source/audio_match[1]).resolve()
        if not audio.is_relative_to(audio_root.resolve()) or any(part.lower() in ('archive', 'archives', 'архів', 'архіви') for part in audio.parts):
            continue
        if not audio.is_file():
            pending.append(transcript.name + ': аудіофайл відсутній')
            continue
        if audio.suffix.lower() != '.m4a':
            raise ValueError('Unsupported audio format: ' + str(audio))
        if not re.search(re.escape('**[') + r'[0-9:]+' + re.escape('] ') + r'[^:]+' + re.escape(':**') + r' +.', text):
            pending.append(transcript.name + ': немає реплік транскрипції')
            continue
        lessons = list((SITE/f'{grade} клас/Робототехніка').glob(f'Урок {number:02} — */*.html'))
        if len(lessons) != 1:
            pending.append(transcript.name + ': урок ще не додано до сайту')
            continue
        key = f'grade-{grade}-lesson-{number:02}'
        description = re.search(r'<meta name="description" content="([^"]*)"', lessons[0].read_text(encoding='utf-8'))
        summary = existing.get(key, {}).get('summary') or (html.unescape(description[1]) if description else f'Аудіорозмова до уроку «{title}». Слухай та читай транскрипцію.')
        (SITE/'podcasts/audio').mkdir(parents=True, exist_ok=True)
        (SITE/'podcasts'/key).mkdir(parents=True, exist_ok=True)
        shutil.copy2(audio, SITE/'podcasts/audio'/f'{key}.m4a')
        shutil.copy2(transcript, SITE/'podcasts'/key/'transcript.md')
        ready.append(dict(id=key, grade=grade, number=number, title=title, summary=summary, lesson=lessons[0].relative_to(SITE).as_posix()))
    # Remove only known generated release files for entries no longer ready.
    ids = {r['id'] for r in ready}
    for old in previous:
        key = old['id']
        if key in ids:
            continue
        if not re.fullmatch(r'grade-[5-7]-lesson-[0-9]+', key):
            raise ValueError('Invalid podcast id')
        for relative in (f'podcasts/audio/{key}.m4a', f'podcasts/{key}/index.html', f'podcasts/{key}/transcript.md'):
            (SITE/relative).unlink(missing_ok=True)
        lesson = (SITE/old['lesson']).resolve()
        if not lesson.is_relative_to(SITE):
            raise ValueError('Lesson outside site')
        if lesson.exists():
            write(lesson, re.sub(r'<!-- podcast:start -->.*?<!-- podcast:end -->', '', lesson.read_text(encoding='utf-8'), flags=re.S))
    write(manifest, json.dumps(ready, ensure_ascii=False, indent=2))
    for message in pending:
        print('Skipped: ' + message)

def build():
    sync_ready_podcasts()
    records=json.loads((SITE/'podcasts/manifest.json').read_text(encoding='utf-8'))
    def shell(title, body, prefix='../'):
        nav=''.join(f'<a href="{prefix}{url(str(g)+" клас")}/index.html">{g} клас</a>' for g in (5,6,7))
        return f'<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Лабораторія робототехніки</title><link rel="stylesheet" href="{prefix}assets/site.css"><link rel="stylesheet" href="{prefix}assets/podcasts.css"><script src="{prefix}assets/podcasts.js" defer></script></head><body><a class="skip" href="#main">До вмісту</a><header><a class="brand" href="{prefix}index.html"><span class="mark">R/00</span>Лабораторія робототехніки</a><span class="small">Слухай · Досліджуй · Створюй</span></header><div class="layout"><aside><div class="eyebrow">Твій маршрут</div><nav aria-label="Розділи"><a href="{prefix}index.html">Усі класи</a>{nav}<a href="{prefix}podcasts/index.html" aria-current="page">Подкасти</a></nav></aside><main id="main">{body}<footer>Лабораторія робототехніки · Навчальні подкасти</footer></main></div></body></html>'
    cards=[]
    for r in records:
        audio=f'audio/{r["id"]}.m4a'
        link=url('../'+r['lesson'])
        transcript=SITE/'podcasts'/r['id']/'transcript.md'
        rows=[]
        if transcript.exists():
            for clock, speaker, text in re.findall(r'\*\*\[([\d:]+)\] ([^:]+):\*\*\s*(.*?)(?=\n\s*\n|\Z)',transcript.read_text(encoding='utf-8'),re.S):
                seconds=0
                for n in clock.split(':'): seconds=seconds*60+int(n)
                rows.append(f'<article class="utterance" data-start="{seconds}"><div><strong>{esc(speaker)}</strong> <button class="time" data-time="{seconds}" aria-label="Слухати з {clock}">{clock}</button></div><p>{esc(text)}</p></article>')
            if not rows: raise ValueError('No transcript rows: '+r['id'])
        transcript_body=('<h2>Транскрипція</h2><p class="small">Автоматична транскрипція Whisper; розподіл голосів виконано алгоритмічно. Текст може містити неточності.</p><label for="transcript-search">Пошук у тексті</label><input id="transcript-search" type="search" placeholder="Знайти слово або фразу"><p id="transcript-status" class="small" role="status"></p><div id="transcript">'+''.join(rows)+'</div>') if rows else '<h2>Транскрипція</h2><p>Транскрипцію ще не додано.</p>'
        body=f'<p class="breadcrumb"><a href="../index.html">Усі подкасти</a> / {r["grade"]} клас</p><section class="hero"><div class="eyebrow">Подкаст · Урок {r["number"]:02}</div><h1>{esc(r["title"])}</h1><p class="lead">{esc(r["summary"])}</p><audio id="podcast-audio" controls preload="metadata" src="../{audio}" aria-label="Подкаст: {esc(r["title"])}">Ваш браузер не підтримує аудіо.</audio><p class="podcast-links"><a href="{url("../../"+r["lesson"])}">Відкрити урок →</a><a href="../{audio}" download>Завантажити аудіо</a></p><p class="audio-status" role="status"></p></section>{transcript_body}'
        write(SITE/'podcasts'/r['id']/'index.html',shell(r['title'],body,'../../'))
        cards.append(f'<article class="card podcast-card" data-grade="{r["grade"]}" data-search="{esc(r["title"].lower())}"><span class="tag">{r["grade"]} клас · Урок {r["number"]:02}</span><h2>{esc(r["title"])}</h2><p>{esc(r["summary"])}</p><audio controls preload="none" src="{audio}" aria-label="Подкаст: {esc(r["title"])}"></audio><p class="audio-status" role="status"></p><div class="podcast-links"><a class="button" href="{r["id"]}/index.html">{"Транскрипція" if rows else "Сторінка подкасту"} →</a><a href="{link}">До уроку</a></div></article>')
        lesson=SITE/r['lesson']
        content=lesson.read_text(encoding='utf-8')
        content=re.sub(r'<!-- podcast:start -->.*?<!-- podcast:end -->','',content,flags=re.S)
        block=f'<!-- podcast:start --><style>.lesson-podcast{{max-width:1152px;margin:12px auto;padding:8px 14px;border:1px solid #d5dfe8;border-radius:12px;background:#edf6f3;display:flex;align-items:center;gap:12px;box-sizing:border-box}}.lesson-podcast .podcast-label{{font-size:14px;font-weight:650;white-space:nowrap}}.lesson-podcast audio{{flex:1;min-width:180px;width:100%;height:32px;margin:0}}.lesson-podcast .podcast-shortcuts{{display:flex;gap:12px;white-space:nowrap;font-size:14px}}@media(max-width:650px){{.lesson-podcast{{margin:10px 16px;flex-wrap:wrap;gap:6px 12px}}.lesson-podcast audio{{order:3;flex-basis:100%}}.lesson-podcast .podcast-shortcuts{{margin-left:auto;font-size:13px}}}}@media print{{.lesson-podcast{{display:none}}}}</style><section class="lesson-podcast" aria-label="Подкаст до уроку"><span class="podcast-label">Подкаст</span><audio controls preload="none" src="../../../podcasts/{audio}" aria-label="Подкаст: {esc(r["title"])}"></audio><div class="podcast-shortcuts"><a href="../../../podcasts/{r["id"]}/index.html">{"Транскрипція" if rows else "Про запис"}</a><a href="../../../podcasts/index.html">Усі подкасти</a></div></section><!-- podcast:end -->'
        nav=re.search(r'<div id="site-navigation".*?</div>',content,re.S)
        pos=nav.end() if nav else content.index('</header>')+len('</header>')
        write(lesson,content[:pos]+block+content[pos:])
    body='<section class="hero"><div class="eyebrow">Аудіолабораторія · 5–7 класи</div><h1>Уроки, які можна слухати</h1><p class="lead">Обери тему, слухай розмову та повертайся до практики. Читай транскрипцію й переходь до потрібного моменту запису.</p></section><div class="podcast-toolbar"><label>Пошук подкасту<input id="podcast-search" type="search" placeholder="Назва або тема"></label><label>Клас<select id="podcast-grade"><option value="">Усі класи</option><option value="5">5 клас</option><option value="6">6 клас</option><option value="7">7 клас</option></select></label></div><p id="podcast-count" class="small" role="status"></p><div class="lessons">'+''.join(cards)+'</div><p id="podcast-empty" hidden>Подкастів за цим запитом немає. Спробуй інше слово або клас.</p>'
    write(SITE/'podcasts/index.html',shell('Подкасти',body))
    print(f'Built {len(records)} podcasts and lesson players.')
if __name__=='__main__': build()
