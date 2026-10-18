const state = { leads: [] };

const els = {
  list: document.querySelector('#lead-list'),
  empty: document.querySelector('#empty-state'),
  input: document.querySelector('#search-input'),
  count: document.querySelector('#result-count'),
  updated: document.querySelector('#last-updated')
};

const formatDate = (value, withTime = false) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '日付不明';
  return new Intl.DateTimeFormat('ja-JP', {
    timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit',
    ...(withTime ? { hour: '2-digit', minute: '2-digit' } : {})
  }).format(date);
};

const escapeHtml = (value = '') => value.replace(/[&<>'"]/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
}[char]));

function render(leads) {
  els.count.textContent = String(leads.length);
  els.empty.hidden = leads.length !== 0;
  els.list.hidden = leads.length === 0;
  els.list.innerHTML = leads.map((lead, index) => `
    <article class="lead-card">
      <div class="lead-meta"><strong>#${String(index + 1).padStart(3, '0')}</strong><span>${formatDate(lead.added_utc)}</span></div>
      <div><h3>${escapeHtml(lead.title)}</h3><p>${escapeHtml(lead.summary || '概要は原典でご確認ください。')}</p></div>
      <a class="source-link" href="${escapeHtml(lead.source_url)}" target="_blank" rel="noopener noreferrer" aria-label="${escapeHtml(lead.title)}の原典を新しいタブで開く">原典を見る ↗</a>
    </article>`).join('');
}

function filterLeads() {
  const query = els.input.value.trim().toLocaleLowerCase();
  const filtered = !query ? state.leads : state.leads.filter(lead =>
    `${lead.title} ${lead.summary || ''}`.toLocaleLowerCase().includes(query)
  );
  render(filtered);
}

async function loadLeads() {
  try {
    const response = await fetch('data/leads.json', { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data)) throw new Error('Invalid data');
    state.leads = data.slice().reverse();
    const newest = state.leads.map(lead => lead.added_utc).filter(Boolean).sort().at(-1);
    els.updated.textContent = newest ? `${formatDate(newest, true)} JST` : 'データなし';
    render(state.leads);
  } catch (error) {
    els.count.textContent = '0';
    els.updated.textContent = '取得できませんでした';
    els.list.innerHTML = '<p class="error-state">データを読み込めませんでした。時間をおいて再度お試しください。</p>';
    console.error('Failed to load leads:', error);
  }
}

els.input.addEventListener('input', filterLeads);
document.addEventListener('keydown', event => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    els.input.focus();
  }
});

loadLeads();
