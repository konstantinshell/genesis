#!/usr/bin/env python3
"""Generate Neiry Metrics HTML pages from markdown source."""
import re, os, html as h

SRC = "/Users/konstantin/Documents/Obsidian Vault/neiry-metrics-guide.md"
OUT = "/Users/konstantin/Documents/nihilo-site/blog/neiry-metrics"

with open(SRC, "r") as f:
    raw = f.read()

# ── PARSE SECTIONS AND METRICS ──
sections_order = [
    ("rhythms", "Ритмы мозга", "c-rhythms", "#7C3AED"),
    ("peaks", "Пиковые частоты", "c-peaks", "#3B82F6"),
    ("alpha-profile", "Альфа-профиль", "c-alpha", "#8B5CF6"),
    ("cognitive", "Когнитивные метрики", "c-cognitive", "#EC4899"),
    ("indices", "Производные индексы", "c-indices", "#F59E0B"),
    ("ppg", "Сердечно-сосудистые (PPG)", "c-ppg", "#EF4444"),
    ("states", "Итоговые статусы", "c-states", "#10B981"),
    ("technical", "Технические метрики", "c-tech", "#6B7280"),
]

# Section boundaries in MD
section_headers = [
    "## Ритмы мозга (Rhythms)",
    "## Мгновенные пиковые частоты (Instant Frequency Peaks)",
    "## Индивидуальный альфа-профиль (Individual Alpha Range)",
    "## Когнитивно-эмоциональные метрики (Emotions)",
    "## Производные индексы",
    "## Сердечно-сосудистые метрики (PPG)",
    "## Итоговые статусы (State Characteristics)",
    "## Технические метрики (для владельцев Neiry и работающих в капсуле)",
]

# Section intro texts (text after ## header before first ###)
section_intros = {
    0: "Значения ритмов нормализованы от 0 до 1, их сумма ≈ 1.0. Ритмы конкурируют друг с другом в общем спектре: если один растёт — другие уступают. Это фундаментальный принцип для понимания всех производных индексов.",
    1: 'В отличие от ритмов (Rhythms), которые показывают «громкость» каждого диапазона, пиковые частоты показывают <strong>качество</strong> ритма — на какой конкретной частоте внутри диапазона находится максимум энергии. Это более тонкий диагностический инструмент.<br><br><em>Критическое правило: Не интерпретируйте пик, если мощность соответствующего ритма &lt; 0.05. Это фантомный пик в шуме, у него нет физиологического смысла.</em>',
    2: "Блок персонального нейрофизиологического паспорта. Эти метрики определяются при калибровке и остаются относительно стабильными на протяжении жизни.",
    3: "Составные метрики, интегрирующие данные ЭЭГ, HRV и персональный baseline. Это самые «высокоуровневые» показатели — они уже интерпретированы для конкретного пользователя.",
    4: "Все индексы — производные от спектральных мощностей ритмов. Они персонализируются через baseline после калибровки.",
    5: "Метрики, получаемые из фотоплетизмографии (PPG) — оптического датчика, измеряющего пульсацию крови в сосудах.",
    6: "",
    7: "Этот раздел предназначен для технических специалистов, владельцев устройств Neiry и тех, кто работает непосредственно в капсуле. Эти метрики не отражают состояние человека — они отражают состояние оборудования и качество данных.",
}

# Extract section content
def get_section_content(idx):
    start_h = section_headers[idx]
    start_pos = raw.find(start_h)
    if start_pos == -1:
        return ""
    start_pos += len(start_h)
    if idx + 1 < len(section_headers):
        end_h = section_headers[idx + 1]
        end_pos = raw.find(end_h)
        if end_pos == -1:
            end_pos = len(raw)
    else:
        # Last section - go to hierarchy or end
        end_pos = raw.find("## Иерархия доверия")
        if end_pos == -1:
            end_pos = len(raw)
    return raw[start_pos:end_pos].strip()

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text[:50]

def parse_metrics(content, is_technical=False):
    """Parse ### metric blocks from section content."""
    metrics = []
    # Split by ### headers
    parts = re.split(r'\n### ', content)
    for part in parts:
        if not part.strip():
            continue
        lines = part.strip().split('\n')
        name = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        if not name:
            continue
        metrics.append((name, body))
    return metrics

def md_to_html_block(name, body, css_class):
    """Convert a metric's markdown body to HTML card."""
    slug = slugify(name)

    # Parse fields from body
    formula = ""
    sections_html = []

    # Extract formula
    fm = re.search(r'\*\*Формула\.\*\*\s*(.+)', body)
    if fm:
        formula = fm.group(1).strip()

    # Field mappings
    field_map = [
        ("Что это за метрика", "ЧТО ЭТО"),
        ("Кто придумал", "КТО ПРИДУМАЛ"),
        ("Кто описал закономерность", "КТО ОПИСАЛ"),
        ("Что измеряет", "ЧТО ИЗМЕРЯЕТ"),
        ("Диапазоны значений", "ДИАПАЗОНЫ"),
        ("Что можно сказать по этой метрике", "ИНТЕРПРЕТАЦИЯ"),
        ("Что можно сказать", "ИНТЕРПРЕТАЦИЯ"),
        ("В каких исследованиях используется", "ИССЛЕДОВАНИЯ"),
        ("В каких исследованиях", "ИССЛЕДОВАНИЯ"),
        ("Когда наблюдать", "КОГДА НАБЛЮДАТЬ"),
        ("Эффекты среды", "ЭФФЕКТЫ СРЕДЫ"),
        ("Критические комбинации", "КРИТИЧЕСКИЕ КОМБИНАЦИИ"),
        ("Ключевое различие SI vs SAT", "SI VS SAT"),
        ("Для чего используется", "ПРИМЕНЕНИЕ"),
        ("Важно", "ВАЖНО"),
        ("Что значит Invalid State", "INVALID STATE"),
        ("Что делать при Invalid State", "ЧТО ДЕЛАТЬ"),
        ("Мифы", "МИФЫ"),
        ("Закрытые глаза, выключены мысли", "ЗАКРЫТЫЕ ГЛАЗА"),
        ("Открытые глаза, фокус на задаче", "ОТКРЫТЫЕ ГЛАЗА, ФОКУС"),
        ("Открытые глаза, фокус", "ОТКРЫТЫЕ ГЛАЗА, ФОКУС"),
    ]

    for field_key, label in field_map:
        pattern = rf'\*\*{re.escape(field_key)}[\.\:]*\*\*\s*([\s\S]*?)(?=\n\*\*[А-ЯA-Z]|\n---|\Z)'
        match = re.search(pattern, body)
        if not match:
            continue

        content = match.group(1).strip()
        if not content or field_key == "Формула":
            continue

        # Convert content to HTML
        content_html = convert_field_content(content, label, field_key)
        sections_html.append(content_html)

    # Build card HTML
    formula_html = f'<div class="metric-formula">{h.escape(formula)}</div>' if formula else ''

    return f'''<div class="metric {css_class}" id="{slug}">
<h3 class="metric-name">{h.escape(name)}</h3>
{formula_html}
{''.join(sections_html)}
</div>'''

def convert_field_content(content, label, field_key):
    """Convert a field's content to HTML."""
    # Handle myths specially
    if field_key == "Мифы":
        myths = re.findall(r'- \*[«"](.+?)[»"]\*\s*(.+?)(?=\n- \*|$)', content, re.DOTALL)
        if myths:
            myth_html = ""
            for myth_text, answer in myths:
                myth_html += f'<div class="myth"><em>«{h.escape(myth_text)}»</em> <strong>{h.escape(answer.strip())}</strong></div>\n'
            return f'<div class="msub"><div class="msub-label">{label}</div>{myth_html}</div>'

    # Handle closed/open eyes
    if "Закрытые глаза" in field_key:
        return f'<div class="state-block eyes-closed"><div class="msub-label">{label}</div><p>{process_inline(content)}</p></div>'
    if "Открытые глаза" in field_key:
        return f'<div class="state-block eyes-open"><div class="msub-label">{label}</div><p>{process_inline(content)}</p></div>'

    # Handle ranges with badges
    if field_key == "Диапазоны значений":
        range_lines = content.strip().split('\n')
        badges_html = ""
        text_html = ""
        for line in range_lines:
            line = line.strip()
            if line.startswith('- '):
                line = line[2:]
                # Try to extract range and description
                parts = line.split(':', 1)
                if len(parts) == 2:
                    range_val = parts[0].strip()
                    desc = parts[1].strip()
                    # Determine badge color
                    color = "gray"
                    lower = desc.lower()
                    if any(w in lower for w in ['норма', 'отлич', 'хорош', 'бодр', 'оптим', 'баланс', 'глубок', 'высок']):
                        color = "green"
                    elif any(w in lower for w in ['умерен', 'средн', 'рабоч', 'обычн', 'лёгк', 'фонов']):
                        color = "blue"
                    elif any(w in lower for w in ['снижен', 'напряж', 'устал', 'выражен', 'повышен', 'внимание', 'рассеян', 'скука', 'высокая нагрузка', 'гипер', 'импульс', 'низк', 'слаб', 'перегрузка', 'перенапр', 'сниж']):
                        color = "yellow"
                    elif any(w in lower for w in ['критич', 'стресс', 'тахикард', 'необходим', 'ненадёжн', 'проблем', 'опасн']):
                        color = "red"
                    badges_html += f'<span class="badge {color}">{h.escape(range_val)}</span> '
                    text_html += f'<li><strong>{h.escape(range_val)}</strong> — {process_inline(desc)}</li>\n'
                else:
                    text_html += f'<li>{process_inline(line)}</li>\n'
            else:
                if line:
                    text_html += f'<p>{process_inline(line)}</p>\n'

        return f'''<div class="msub">
<div class="msub-label">{label}</div>
<div class="ranges">{badges_html}</div>
<ul>{text_html}</ul>
</div>'''

    # Handle bullet lists
    if '\n- ' in content:
        items = content.split('\n- ')
        first = items[0].strip()
        list_items = items[1:]
        out = '<div class="msub"><div class="msub-label">' + label + '</div>'
        if first:
            out += f'<p>{process_inline(first)}</p>'
        out += '<ul>'
        for item in list_items:
            out += f'<li>{process_inline(item.strip())}</li>'
        out += '</ul></div>'
        return out

    # Default paragraph
    paragraphs = content.strip().split('\n\n')
    p_html = ''.join(f'<p>{process_inline(p.strip())}</p>' for p in paragraphs if p.strip())
    return f'<div class="msub"><div class="msub-label">{label}</div>{p_html}</div>'

def process_inline(text):
    """Convert inline markdown to HTML."""
    text = text.replace('\n', ' ')
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def page_head(title):
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — ONTO NOTHING</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../css/nav.css">
<link rel="stylesheet" href="./metrics.css">
</head>
<body>
'''

def page_foot():
    return '''
<script src="../../components/nav.js"></script>
<script src="../../components/footer.js"></script>
</body>
</html>'''

def section_nav_html(current_idx):
    """Generate sticky nav for section page."""
    nav = '<nav class="sticky-header"><div class="block-nav"><div class="block-nav-inner">\n'
    nav += '<a href="./index.html" class="block-nav-btn" style="font-weight:500;color:var(--text)">← Все метрики</a>\n'
    for i, (slug, name, css, color) in enumerate(sections_order):
        style = 'font-weight:600;color:var(--text)' if i == current_idx else ''
        nav += f'<a href="./{slug}.html" class="block-nav-btn" style="{style}"><span class="block-nav-dot" style="background:{color}"></span>{h.escape(name)}</a>\n'
    nav += '</div></div></nav>\n'
    return nav

# ═══════════════════════════════════════════════
# GENERATE HUB PAGE
# ═══════════════════════════════════════════════
hub_html = page_head("Справочник метрик Neiry Capsule")
hub_html += '''
<section class="hero">
<div class="hero-inner">
<div class="hero-eyebrow">справочник</div>
<h1>Метрики Neiry Capsule</h1>
<p class="hero-sub">Подробный справочник по всем метрикам экосистемы Neiry Capsule — для исследователей, практиков, нейрофизиологов и владельцев устройства.</p>
</div>
</section>

<div class="content">
<div class="hub-grid">
'''

hub_descriptions = {
    0: ("4 метрики", "Alpha, Beta, Theta, SMR — нормализованные мощности мозговых ритмов от 0 до 1."),
    1: ("3 метрики", "Alpha Peak, Beta Peak, Theta Peak — мгновенные пиковые частоты внутри каждого диапазона."),
    2: ("5 метрик", "IAF, IAPF, IAPF Power, IABW, IAPF Suppression — персональный нейрофизиологический паспорт."),
    3: ("4 метрики", "Attention, Relaxation, Cognitive Load, Cognitive Control — высокоуровневые составные показатели."),
    4: ("7 метрик", "Relaxation Index, Concentration Index, Fatigue Score, Reverse Fatigue, Accumulated Fatigue, Productivity Score, Alpha Gravity."),
    5: ("10 метрик", "HR, RR(M), Mo, SDNN, CV, AMo, MxdMn, SI Баевского, SAT Каплана, Perfusion."),
    6: ("3 метрики", "Stress, Recommendation, State — итоговые бинарные и текстовые статусы."),
    7: ("13 метрик", "IsConnected, Battery, Serial, Firmware, Mode, Session, Data Markup, импеданс, Artifacts и др."),
}

for i, (slug, name, css, color) in enumerate(sections_order):
    count, desc = hub_descriptions[i]
    hub_html += f'''<a href="./{slug}.html" class="hub-card {css}">
<div class="hub-count">{count}</div>
<h3>{h.escape(name)}</h3>
<p>{h.escape(desc)}</p>
</a>
'''

hub_html += '</div>\n'

# Trust hierarchy
hub_html += '''
<h2 style="margin-top:48px;font-size:24px">Иерархия доверия к данным</h2>
<p style="color:var(--text2);margin:8px 0 16px">При анализе данных Neiry придерживайтесь следующего порядка проверки:</p>

<div class="trust-level trust-1">
<h4>Уровень 1 — абсолютный приоритет (проверять первым)</h4>
<p>Valid State, Artifacts, Perfusion, PPG quality, Average µV, импеданс электродов. Если здесь проблемы — остальные данные не интерпретируются.</p>
</div>
<div class="trust-level trust-2">
<h4>Уровень 2 — высокая надёжность</h4>
<p>SDNN, SI, Alpha Peak vs IAPF, Accumulated Fatigue. Эти метрики хорошо изучены и надёжны при чистых данных.</p>
</div>
<div class="trust-level trust-3">
<h4>Уровень 3 — средняя надёжность</h4>
<p>Concentration, Relaxation, Fatigue Score. Требуют корректной калибровки для точности.</p>
</div>
<div class="trust-level trust-4">
<h4>Уровень 4 — динамические</h4>
<p>Instant Frequency Peaks, Emotions. Значимы только при устойчивости 2+ минуты. Кратковременные скачки — шум, не сигнал.</p>
</div>

<p style="color:var(--text3);font-size:0.85rem;margin-top:32px;font-style:italic">Этот справочник основан на данных, доступных через экосистему Neiry Capsule. Для профессиональной медицинской диагностики обратитесь к специалисту.</p>
</div>
'''
hub_html += page_foot()

with open(os.path.join(OUT, "index.html"), "w") as f:
    f.write(hub_html)
print("✓ index.html")

# ═══════════════════════════════════════════════
# GENERATE SECTION PAGES
# ═══════════════════════════════════════════════
for idx, (slug, sec_name, css_class, color) in enumerate(sections_order):
    content = get_section_content(idx)
    metrics = parse_metrics(content, is_technical=(idx == 7))
    intro = section_intros.get(idx, "")

    html = page_head(f"{sec_name} — Справочник метрик")
    html += section_nav_html(idx)

    html += f'''
<div class="content">
<a href="./index.html" class="back-link">← Все метрики</a>

<div class="section-intro">
<h2 style="font-size:clamp(24px,4vw,36px)">{h.escape(sec_name)}</h2>
{"<p>" + intro + "</p>" if intro else ""}
</div>
'''

    # Metrics mini-toc
    if metrics:
        html += '<nav style="background:var(--bg3);border-radius:12px;padding:16px 20px;margin-bottom:32px">\n'
        html += '<div style="font-family:DM Mono,monospace;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:var(--text3);margin-bottom:8px">СОДЕРЖАНИЕ</div>\n'
        for name, _ in metrics:
            s = slugify(name)
            html += f'<a href="#{s}" style="display:inline-block;font-size:0.88rem;color:{color};margin:3px 12px 3px 0">{h.escape(name)}</a>\n'
        html += '</nav>\n'

    # Technical section has simpler format
    if idx == 7:
        for name, body in metrics:
            slug_m = slugify(name)
            # Simpler rendering for tech metrics
            body_html = process_inline(body.replace('\n\n', '</p><p>').replace('\n- ', '</li><li>'))
            if '<li>' in body_html:
                body_html = '<ul><li>' + body_html + '</li></ul>'
            else:
                body_html = '<p>' + body_html + '</p>'
            html += f'''<div class="metric c-tech" id="{slug_m}" style="padding:20px 24px">
<h3 class="metric-name" style="font-size:18px">{h.escape(name)}</h3>
{body_html}
</div>
'''
    else:
        for name, body in metrics:
            html += md_to_html_block(name, body, css_class)

    html += '</div>\n'
    html += page_foot()

    filepath = os.path.join(OUT, f"{slug}.html")
    with open(filepath, "w") as f:
        f.write(html)
    print(f"✓ {slug}.html ({len(metrics)} metrics)")

print("\nDone! All pages generated.")
