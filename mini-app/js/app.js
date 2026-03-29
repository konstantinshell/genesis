// Initialize Telegram WebApp
let WebApp;
let userId;

document.addEventListener('DOMContentLoaded', async function() {
    // Initialize Telegram WebApp
    if (window.Telegram && window.Telegram.WebApp) {
        WebApp = window.Telegram.WebApp;
        WebApp.ready();

        // Get user data from Telegram
        const initData = WebApp.initData;
        try {
            const data = new URLSearchParams(initData);
            const userStr = data.get('user');
            if (userStr) {
                const user = JSON.parse(userStr);
                userId = user.id;
            }
        } catch (e) {
            console.warn('Could not parse Telegram init data');
        }
    }

    // Fallback for testing: get user_id from URL params
    if (!userId) {
        const params = new URLSearchParams(window.location.search);
        userId = params.get('user_id') || 'test-user';
    }

    // Setup page navigation
    setupNavigation();

    // Load profile data
    await loadProfileData();
});

// ───────────────────────────────────────────────────────────────
// Navigation
// ───────────────────────────────────────────────────────────────

function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const pages = document.querySelectorAll('.page');

    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const pageName = this.dataset.page;

            // Update active button
            navButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // Show/hide pages
            pages.forEach(page => page.classList.remove('active'));
            document.getElementById(pageName + '-page').classList.add('active');
        });
    });
}

// ───────────────────────────────────────────────────────────────
// Load Profile Data
// ───────────────────────────────────────────────────────────────

async function loadProfileData() {
    const loadingEl = document.getElementById('loading');
    const contentEl = document.getElementById('profile-content');
    const errorEl = document.getElementById('error-message');

    try {
        // Load personal summary: summaries/{telegram_id}.md
        const summaryUrl = `summaries/${userId}.md?t=${Date.now()}`;

        // Try to fetch summary.md
        const response = await fetch(summaryUrl);

        if (!response.ok) {
            throw new Error(`Failed to load summary: ${response.statusText}`);
        }

        const markdown = await response.text();
        const data = parseMarkdown(markdown);

        // Populate UI elements
        populateProfile(data);

        // Hide loading, show content
        loadingEl.style.display = 'none';
        contentEl.style.display = 'block';

    } catch (error) {
        console.error('Error loading profile:', error);

        // Show error message
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
        errorEl.querySelector('#error-text').textContent = error.message;
    }
}

// ───────────────────────────────────────────────────────────────
// Parse Markdown
// ───────────────────────────────────────────────────────────────

function parseMarkdown(markdown) {
    const data = {
        name: '',
        city: '',
        activity: '',
        mnpi: '',
        weeklyTasks: '',
        yearlyGoal: '',
        whatIgnites: '',
        whatBlocks: '',
        neiry: {
            focus: '—',
            relax: '—',
            stress: '—',
            attention: '—'
        },
        lastUpdate: 'сейчас'
    };

    const lines = markdown.split('\n');
    let currentSection = '';
    let currentContent = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // Parse main heading (name)
        if (line.startsWith('# ') && !line.startsWith('# MNPI') && !line.startsWith('# Данные')) {
            data.name = line.replace('# ', '').trim();
        }

        // Parse sections
        if (line.startsWith('## ')) {
            // Save previous section
            if (currentSection) {
                const content = currentContent.join('\n').trim();
                assignSection(data, currentSection, content);
            }

            currentSection = line.replace('## ', '').trim();
            currentContent = [];
        } else if (currentSection) {
            if (line) {
                currentContent.push(line);
            }
        }

        // Parse city and activity from profile section
        if (line.startsWith('👤')) {
            const parts = line.split('—');
            if (parts.length >= 2) {
                data.city = parts[1].trim();
                if (parts.length >= 3) {
                    data.activity = parts[2].trim();
                }
            }
        }

        // Parse NEIRY metrics (looking for patterns like "📊 Метрика: значение")
        if (line.includes('Концентрация') || line.includes('концентрация')) {
            const value = extractMetricValue(line);
            if (value) data.neiry.focus = value;
        }
        if (line.includes('Релаксация') || line.includes('релаксация')) {
            const value = extractMetricValue(line);
            if (value) data.neiry.relax = value;
        }
        if (line.includes('Стресс') || line.includes('стресс')) {
            const value = extractMetricValue(line);
            if (value) data.neiry.stress = value;
        }
        if (line.includes('Внимание') || line.includes('внимание')) {
            const value = extractMetricValue(line);
            if (value) data.neiry.attention = value;
        }

        // Parse last update timestamp
        if (line.includes('Обновлено') || line.includes('обновлено')) {
            const match = line.match(/(\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}:\d{2})/);
            if (match) {
                data.lastUpdate = match[1];
            }
        }
    }

    // Save last section
    if (currentSection) {
        const content = currentContent.join('\n').trim();
        assignSection(data, currentSection, content);
    }

    return data;
}

function assignSection(data, section, content) {
    section = section.toLowerCase();

    if (section.includes('mnpi')) {
        data.mnpi = content;
    } else if (section.includes('задачи') && section.includes('неделя')) {
        data.weeklyTasks = content;
    } else if (section.includes('цель') && section.includes('год')) {
        data.yearlyGoal = content;
    } else if (section.includes('зажигает')) {
        data.whatIgnites = content;
    } else if (section.includes('тормозит')) {
        data.whatBlocks = content;
    }
}

function extractMetricValue(line) {
    // Extract value from patterns like:
    // "📊 Концентрация: 75%"
    // "Концентрация — 75"
    const match = line.match(/[:\-—]\s*([0-9.]+%?|высокая|средняя|низкая)/i);
    return match ? match[1] : null;
}

// ───────────────────────────────────────────────────────────────
// Populate UI
// ───────────────────────────────────────────────────────────────

function populateProfile(data) {
    // Header
    document.getElementById('profile-name').textContent = data.name || 'Профиль';

    const cityText = data.city ? `${data.city}` : 'Город';
    const activityText = data.activity ? `${data.activity}` : 'Деятельность';
    document.getElementById('profile-city').textContent = `${cityText} · ${activityText}`;

    // MNPI
    const mnpiEl = document.getElementById('mnpi-content');
    if (data.mnpi) {
        mnpiEl.innerHTML = formatContentHTML(data.mnpi);
    } else {
        mnpiEl.innerHTML = '<p>Данные загружаются...</p>';
    }

    // Weekly tasks
    const tasksEl = document.getElementById('weekly-tasks');
    if (data.weeklyTasks) {
        tasksEl.innerHTML = formatContentHTML(data.weeklyTasks);
    } else {
        tasksEl.innerHTML = '<p>Задачи появятся после первого обновления</p>';
    }

    // Yearly goal
    const goalEl = document.getElementById('yearly-goal');
    if (data.yearlyGoal) {
        goalEl.innerHTML = formatContentHTML(data.yearlyGoal);
    } else {
        goalEl.innerHTML = '<p>Формируется на основе твоих данных</p>';
    }

    // What ignites
    const igniteEl = document.getElementById('what-ignites');
    if (data.whatIgnites) {
        igniteEl.innerHTML = formatContentHTML(data.whatIgnites);
    } else {
        igniteEl.innerHTML = '<p>Данные появятся после анализа</p>';
    }

    // What blocks
    const blocksEl = document.getElementById('what-blocks');
    if (data.whatBlocks) {
        blocksEl.innerHTML = formatContentHTML(data.whatBlocks);
    } else {
        blocksEl.innerHTML = '<p>Данные появятся после анализа</p>';
    }

    // NEIRY Metrics
    document.getElementById('metric-focus').textContent = data.neiry.focus;
    document.getElementById('metric-relax').textContent = data.neiry.relax;
    document.getElementById('metric-stress').textContent = data.neiry.stress;
    document.getElementById('metric-attention').textContent = data.neiry.attention;

    // Last update
    document.getElementById('last-update').textContent = data.lastUpdate;
}

function formatContentHTML(markdown) {
    // Simple markdown to HTML conversion
    let html = markdown;

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Code blocks
    html = html.replace(/`([^`]+)`/g, '<code style="background: rgba(95,95,255,0.1); padding: 2px 6px; border-radius: 3px; font-family: monospace;">$1</code>');

    // Lists
    const listRegex = /[\n\r][-*]\s+(.+?)(?=[\n\r][-*]|[\n\r]|$)/g;
    if (listRegex.test(html)) {
        html = html.replace(/[\n\r][-*]\s+/g, '\n<li>');
        html = html.replace(/\n<li>/g, '\n  <li>');
        html = '<ul style="margin: 12px 0; padding-left: 20px;">' + html + '\n</ul>';
    }

    // Line breaks to <br>
    html = html.replace(/\n\n/g, '</p><p>');
    if (!html.startsWith('<p>')) {
        html = '<p>' + html;
    }
    if (!html.endsWith('</p>')) {
        html = html + '</p>';
    }

    return html;
}

// ───────────────────────────────────────────────────────────────
// Theme Support (Telegram Dark Mode)
// ───────────────────────────────────────────────────────────────

if (window.Telegram && window.Telegram.WebApp) {
    document.addEventListener('themeChanged', function() {
        const theme = WebApp.colorScheme;
        document.documentElement.style.colorScheme = theme;
    });
}
