#!/usr/bin/env python3
"""Generate Neiry Metrics HTML pages — 3-level structure:
   Hub (index.html) → Section hubs (rhythms.html) → Metric pages (rhythms/alpha.html)
"""
import re, os, html as h, shutil

SRC = "/Users/konstantin/Documents/Obsidian Vault/neiry-metrics-guide.md"
OUT = "/Users/konstantin/Documents/nihilo-site/blog/neiry-metrics"

with open(SRC, "r") as f:
    raw = f.read()

# ══════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════
sections = [
    {
        "slug": "rhythms",
        "name": "Ритмы мозга",
        "css": "c-rhythms",
        "color": "#7C3AED",
        "header": "## Ритмы мозга (Rhythms)",
        "intro": "Значения ритмов нормализованы от 0 до 1, их сумма ≈ 1.0. Ритмы конкурируют друг с другом в общем спектре: если один растёт — другие уступают.",
        "has_subpages": True,
    },
    {
        "slug": "peaks",
        "name": "Пиковые частоты",
        "css": "c-peaks",
        "color": "#3B82F6",
        "header": "## Мгновенные пиковые частоты (Instant Frequency Peaks)",
        "intro": "Пиковые частоты показывают качество ритма — на какой конкретной частоте находится максимум энергии. Не интерпретируйте пик, если мощность ритма &lt; 0.05.",
        "has_subpages": True,
    },
    {
        "slug": "alpha-profile",
        "name": "Альфа-профиль",
        "css": "c-alpha",
        "color": "#8B5CF6",
        "header": "## Индивидуальный альфа-профиль (Individual Alpha Range)",
        "intro": "Персональный нейрофизиологический паспорт. Эти метрики определяются при калибровке и остаются стабильными на протяжении жизни.",
        "has_subpages": True,
    },
    {
        "slug": "cognitive",
        "name": "Когнитивные метрики",
        "css": "c-cognitive",
        "color": "#EC4899",
        "header": "## Когнитивно-эмоциональные метрики (Emotions)",
        "intro": "Составные метрики, интегрирующие данные ЭЭГ, HRV и персональный baseline — самые высокоуровневые показатели.",
        "has_subpages": True,
    },
    {
        "slug": "indices",
        "name": "Производные индексы",
        "css": "c-indices",
        "color": "#F59E0B",
        "header": "## Производные индексы",
        "intro": "Производные от спектральных мощностей ритмов. Персонализируются через baseline после калибровки.",
        "has_subpages": True,
    },
    {
        "slug": "ppg",
        "name": "Сердечно-сосудистые (PPG)",
        "css": "c-ppg",
        "color": "#EF4444",
        "header": "## Сердечно-сосудистые метрики (PPG)",
        "intro": "Метрики из фотоплетизмографии (PPG) — оптического датчика, измеряющего пульсацию крови в сосудах.",
        "has_subpages": True,
    },
    {
        "slug": "states",
        "name": "Итоговые статусы",
        "css": "c-states",
        "color": "#10B981",
        "header": "## Итоговые статусы (State Characteristics)",
        "intro": "",
        "has_subpages": True,
    },
    {
        "slug": "technical",
        "name": "Технические метрики",
        "css": "c-tech",
        "color": "#6B7280",
        "header": "## Технические метрики (для владельцев Neiry и работающих в капсуле)",
        "intro": "Для технических специалистов и владельцев устройств. Отражают состояние оборудования и качество данных.",
        "has_subpages": False,
    },
]

# ══════════════════════════════════════════════
# PARSING
# ══════════════════════════════════════════════
def get_section_content(sec):
    start_pos = raw.find(sec["header"])
    if start_pos == -1:
        return ""
    start_pos += len(sec["header"])
    idx = next(i for i, s in enumerate(sections) if s["slug"] == sec["slug"])
    if idx + 1 < len(sections):
        end_pos = raw.find(sections[idx + 1]["header"])
        if end_pos == -1:
            end_pos = len(raw)
    else:
        end_pos = raw.find("## Иерархия доверия")
        if end_pos == -1:
            end_pos = len(raw)
    return raw[start_pos:end_pos].strip()

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text[:50]

SLUG_MAP = {
    "Alpha (8–13 Гц)": "alpha",
    "Beta (13–30 Гц)": "beta",
    "Theta (4–8 Гц)": "theta",
    "SMR — сенсомоторный ритм (12–15 Гц)": "smr",
    "Alpha Peak": "alpha-peak",
    "Beta Peak": "beta-peak",
    "Theta Peak": "theta-peak",
    "IAF — индивидуальная альфа-частота": "iaf",
    "IAPF — частота максимального альфа-пика": "iapf",
    "IAPF Power — мощность альфа-пика": "iapf-power",
    "IABW — ширина альфа-диапазона": "iabw",
    "IAPF Suppression — коэффициент подавления": "iapf-suppression",
    "Attention": "attention",
    "Relaxation": "relaxation",
    "Cognitive Load": "cognitive-load",
    "Cognitive Control": "cognitive-control",
    "Relaxation Index": "relaxation-index",
    "Concentration Index": "concentration-index",
    "Fatigue Score": "fatigue-score",
    "Reverse Fatigue": "reverse-fatigue",
    "Accumulated Fatigue": "accumulated-fatigue",
    "Productivity Score": "productivity-score",
    "Alpha Gravity": "alpha-gravity",
    "HR — частота сердечных сокращений": "hr",
    "RR(M) — средний кардиоинтервал": "rrm",
    "Mo — мода кардиоинтервалов": "mo",
    "SDNN": "sdnn",
    "CV — коэффициент вариации": "cv",
    "AMo — амплитуда моды": "amo",
    "MxdMn — вариационный размах": "mxdmn",
    "SI — стресс-индекс Баевского": "si",
    "SAT — индекс Каплана": "sat",
    "Perfusion — индекс перфузии": "perfusion",
    "Stress": "stress",
    "Recommendation": "recommendation",
    "State": "state",
}

def metric_file_slug(name):
    if name in SLUG_MAP:
        return SLUG_MAP[name]
    # Fallback
    s = name.lower()
    for old, new in [("—", ""), ("(", ""), (")", ""), ("  ", " ")]:
        s = s.replace(old, new)
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s.strip())
    return s[:40] or "metric"

def parse_metrics(content):
    metrics = []
    parts = re.split(r'\n### ', content)
    for part in parts:
        if not part.strip():
            continue
        lines = part.strip().split('\n')
        name = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        if not name:
            continue
        # Skip if name looks like intro text (too long, no metric-like pattern)
        if len(name) > 80:
            continue
        # Skip intro paragraphs that have no body content at all
        if not body.strip():
            continue
        metrics.append({"name": name, "body": body, "slug": metric_file_slug(name)})
    return metrics

def extract_first_sentence(body):
    """Extract first sentence from 'Что это за метрика' field."""
    m = re.search(r'\*\*Что это за метрика[\.\:]*\*\*\s*(.+?)(?:\.|$)', body)
    if m:
        return m.group(1).strip() + "."
    # Fallback: first non-empty line
    for line in body.split('\n'):
        line = line.strip()
        if line and not line.startswith('**') and not line.startswith('---'):
            return line[:120]
    return ""

def extract_formula(body):
    m = re.search(r'\*\*Формула\.\*\*\s*(.+)', body)
    return m.group(1).strip() if m else ""

def extract_ranges_badges(body):
    """Extract range badges for summary cards."""
    m = re.search(r'\*\*Диапазоны значений[\.\:]*\*\*\s*([\s\S]*?)(?=\n\*\*[А-ЯA-Z]|\n---|\Z)', body)
    if not m:
        return ""
    content = m.group(1).strip()
    badges = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- '):
            parts = line[2:].split(':', 1)
            if len(parts) == 2:
                range_val = parts[0].strip()
                desc = parts[1].strip().lower()
                color = "gray"
                if any(w in desc for w in ['норма', 'отлич', 'хорош', 'бодр', 'оптим', 'баланс', 'глубок']):
                    color = "green"
                elif any(w in desc for w in ['умерен', 'средн', 'рабоч', 'обычн', 'лёгк', 'фонов']):
                    color = "blue"
                elif any(w in desc for w in ['снижен', 'напряж', 'устал', 'выражен', 'повышен', 'рассеян', 'скука', 'перегрузка', 'гипер', 'импульс', 'низк', 'слаб']):
                    color = "yellow"
                elif any(w in desc for w in ['критич', 'стресс', 'тахикард', 'необходим', 'ненадёжн', 'проблем']):
                    color = "red"
                badges.append(f'<span class="badge {color}">{h.escape(range_val)}</span>')
    return ' '.join(badges[:4])

# ══════════════════════════════════════════════
# HTML HELPERS
# ══════════════════════════════════════════════
def process_inline(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text

def convert_field_content(content, label, field_key):
    if field_key == "Мифы":
        myths = re.findall(r'- \*[«"](.+?)[»"]\*\s*(.+?)(?=\n- \*|$)', content, re.DOTALL)
        if myths:
            myth_html = ""
            for myth_text, answer in myths:
                myth_html += f'<div class="myth"><em>«{h.escape(myth_text)}»</em> <strong>{h.escape(answer.strip())}</strong></div>\n'
            return f'<div class="msub"><div class="msub-label">{label}</div>{myth_html}</div>'

    if "Закрытые глаза" in field_key:
        return f'<div class="state-block eyes-closed"><div class="msub-label">{label}</div><p>{process_inline(content)}</p></div>'
    if "Открытые глаза" in field_key:
        return f'<div class="state-block eyes-open"><div class="msub-label">{label}</div><p>{process_inline(content)}</p></div>'

    if field_key == "Диапазоны значений":
        range_lines = content.strip().split('\n')
        badges_html = ""
        text_html = ""
        for line in range_lines:
            line = line.strip()
            if line.startswith('- '):
                line = line[2:]
                parts = line.split(':', 1)
                if len(parts) == 2:
                    range_val = parts[0].strip()
                    desc = parts[1].strip()
                    color = "gray"
                    lower = desc.lower()
                    if any(w in lower for w in ['норма', 'отлич', 'хорош', 'бодр', 'оптим', 'баланс', 'глубок', 'высок']):
                        color = "green"
                    elif any(w in lower for w in ['умерен', 'средн', 'рабоч', 'обычн', 'лёгк', 'фонов']):
                        color = "blue"
                    elif any(w in lower for w in ['снижен', 'напряж', 'устал', 'выражен', 'повышен', 'внимание', 'рассеян', 'скука', 'высокая нагрузка', 'гипер', 'импульс', 'низк', 'слаб', 'перенапр', 'сниж']):
                        color = "yellow"
                    elif any(w in lower for w in ['критич', 'стресс', 'тахикард', 'необходим', 'ненадёжн', 'проблем', 'опасн']):
                        color = "red"
                    badges_html += f'<span class="badge {color}">{h.escape(range_val)}</span> '
                    text_html += f'<li><strong>{h.escape(range_val)}</strong> — {process_inline(desc)}</li>\n'
                else:
                    text_html += f'<li>{process_inline(line)}</li>\n'
            elif line:
                text_html += f'<p>{process_inline(line)}</p>\n'
        return f'<div class="msub"><div class="msub-label">{label}</div><div class="ranges">{badges_html}</div><ul>{text_html}</ul></div>'

    if '\n- ' in content:
        items = content.split('\n- ')
        first = items[0].strip()
        list_items = items[1:]
        out = f'<div class="msub"><div class="msub-label">{label}</div>'
        if first:
            out += f'<p>{process_inline(first)}</p>'
        out += '<ul>' + ''.join(f'<li>{process_inline(item.strip())}</li>' for item in list_items) + '</ul></div>'
        return out

    paragraphs = content.strip().split('\n\n')
    p_html = ''.join(f'<p>{process_inline(p.strip())}</p>' for p in paragraphs if p.strip())
    return f'<div class="msub"><div class="msub-label">{label}</div>{p_html}</div>'

def build_metric_html(metric, css_class):
    body = metric["body"]
    formula = extract_formula(body)
    sections_html = []

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
        sections_html.append(convert_field_content(content, label, field_key))

    formula_html = f'<div class="metric-formula">{h.escape(formula)}</div>' if formula else ''
    return f'''<div class="metric {css_class}">
<h3 class="metric-name">{h.escape(metric["name"])}</h3>
{formula_html}
{''.join(sections_html)}
</div>'''

def page_head(title, css_path="./metrics.css", nav_path="../../css/nav.css"):
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — ONTO NOTHING</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{nav_path}">
<link rel="stylesheet" href="{css_path}">
</head>
<body>
'''

def page_foot(nav_script="../../components/nav.js", footer_script="../../components/footer.js"):
    return f'''
<script src="{nav_script}"></script>
<script src="{footer_script}"></script>
</body>
</html>'''

# ══════════════════════════════════════════════
# GENERATE SECTION HUB PAGES
# ══════════════════════════════════════════════
for sec in sections:
    content = get_section_content(sec)
    metrics = parse_metrics(content)
    sec["metrics"] = metrics

    if not sec["has_subpages"]:
        # Technical page — keep as flat list
        page = page_head(f"{sec['name']} — Справочник метрик")
        page += f'''
<div class="content">
<div class="breadcrumbs">
<a href="./index.html">Все метрики</a> <span class="sep">→</span> <span>{h.escape(sec["name"])}</span>
</div>
<div class="section-intro">
<h2 style="font-size:clamp(24px,4vw,36px)">{h.escape(sec["name"])}</h2>
{"<p>" + sec["intro"] + "</p>" if sec["intro"] else ""}
</div>
'''
        for m in metrics:
            body_html = process_inline(m["body"].replace('\n\n', '</p><p>').replace('\n- ', '</li><li>'))
            if '<li>' in body_html:
                body_html = '<ul><li>' + body_html + '</li></ul>'
            else:
                body_html = '<p>' + body_html + '</p>'
            page += f'''<div class="metric c-tech" style="padding:20px 24px">
<h3 class="metric-name" style="font-size:18px">{h.escape(m["name"])}</h3>
{body_html}
</div>
'''
        page += '</div>'
        page += page_foot()
        with open(os.path.join(OUT, f"{sec['slug']}.html"), "w") as f:
            f.write(page)
        print(f"✓ {sec['slug']}.html (flat, {len(metrics)} metrics)")
        continue

    # Section hub page — grid of metric summary cards
    page = page_head(f"{sec['name']} — Справочник метрик")
    page += f'''
<div class="content">
<div class="breadcrumbs">
<a href="./index.html">Все метрики</a> <span class="sep">→</span> <span>{h.escape(sec["name"])}</span>
</div>
<div class="section-intro">
<h2 style="font-size:clamp(24px,4vw,36px)">{h.escape(sec["name"])}</h2>
{"<p style='color:var(--text2);margin-top:8px'>" + sec["intro"] + "</p>" if sec["intro"] else ""}
</div>

<div class="metrics-grid">
'''
    for m in metrics:
        summary = extract_first_sentence(m["body"])
        formula = extract_formula(m["body"])
        badges = extract_ranges_badges(m["body"])
        formula_html = f'<div class="metric-formula">{h.escape(formula)}</div>' if formula else ''
        badges_html = f'<div class="ranges">{badges}</div>' if badges else ''

        page += f'''<a href="./{sec["slug"]}/{m["slug"]}.html" class="metric-summary {sec["css"]}">
<h3>{h.escape(m["name"])}</h3>
{formula_html}
<p>{process_inline(summary)}</p>
{badges_html}
</a>
'''

    page += '</div>\n</div>'
    page += page_foot()

    with open(os.path.join(OUT, f"{sec['slug']}.html"), "w") as f:
        f.write(page)
    print(f"✓ {sec['slug']}.html (hub, {len(metrics)} cards)")

# ══════════════════════════════════════════════
# GENERATE INDIVIDUAL METRIC PAGES
# ══════════════════════════════════════════════
for sec in sections:
    if not sec["has_subpages"]:
        continue

    metrics = sec["metrics"]
    subdir = os.path.join(OUT, sec["slug"])
    os.makedirs(subdir, exist_ok=True)

    for i, m in enumerate(metrics):
        # Build prev/next navigation
        prev_link = ""
        next_link = ""
        if i > 0:
            prev_m = metrics[i - 1]
            prev_link = f'''<a href="./{prev_m["slug"]}.html">
<span class="nav-dir">← Назад</span>
<span class="nav-name">{h.escape(prev_m["name"])}</span>
</a>'''
        if i < len(metrics) - 1:
            next_m = metrics[i + 1]
            next_link = f'''<a href="./{next_m["slug"]}.html" class="next">
<span class="nav-dir">Далее →</span>
<span class="nav-name">{h.escape(next_m["name"])}</span>
</a>'''

        metric_content = build_metric_html(m, sec["css"])

        page = page_head(
            f'{m["name"]} — {sec["name"]}',
            css_path="../metrics.css",
            nav_path="../../../css/nav.css"
        )
        page += f'''
<div class="content">
<div class="breadcrumbs">
<a href="../index.html">Все метрики</a>
<span class="sep">→</span>
<a href="../{sec["slug"]}.html">{h.escape(sec["name"])}</a>
<span class="sep">→</span>
<span>{h.escape(m["name"])}</span>
</div>

{metric_content}

<div class="metric-nav">
{prev_link}
{next_link}
</div>
</div>
'''
        page += page_foot(
            nav_script="../../../components/nav.js",
            footer_script="../../../components/footer.js"
        )

        filepath = os.path.join(subdir, f"{m['slug']}.html")
        with open(filepath, "w") as f:
            f.write(page)

    print(f"  ✓ {sec['slug']}/ ({len(metrics)} metric pages)")

print("\nDone! All pages generated.")
