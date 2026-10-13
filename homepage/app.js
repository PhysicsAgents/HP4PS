const LOCALES = { en: 'en_US', zh: 'zh_CN' };
const LANG_KEY = 'hp4ps.lang';
const LEVELS = ['domain', 'subfield', 'branch', 'researchPath', 'technicalPath'];
const LINKS = ['github', 'huggingface', 'dockerhub'];
const REVIEWER_TITLES = ['graduate', 'phd', 'professor'];

const loadJson = async (path) => {
  try {
    const response = await fetch(path);
    return response.ok ? await response.json() : null;
  } catch {
    return null;
  }
};

const storage = {
  get: (key) => { try { return localStorage.getItem(key); } catch { return null; } },
  set: (key, value) => { try { localStorage.setItem(key, value); } catch {} },
};

const lookup = (dict, key) => key.split('.').reduce((node, part) => node?.[part], dict);

const h = (tag, attrs = {}, ...children) => {
  const el = document.createElement(tag);
  Object.entries(attrs).forEach(([name, value]) => el.setAttribute(name, value));
  el.append(...children.flat().filter((child) => child !== null && child !== undefined));
  return el;
};

const empty = (text) => h('p', { class: 'empty' }, text);

const initialLang = () => {
  const saved = storage.get(LANG_KEY);
  if (saved in LOCALES) return saved;
  return navigator.language?.toLowerCase().startsWith('zh') ? 'zh' : 'en';
};

const renderLinks = (t, links) =>
  LINKS.map((name) =>
    links?.[name]
      ? h('a', { class: 'button', href: links[name], rel: 'noopener' }, t(`links.${name}`))
      : h('span', { class: 'button disabled', title: t('links.pending') }, t(`links.${name}`)));

const renderLevels = (t) => LEVELS.map((level) => h('li', {}, t(`taxonomy.levels.${level}`)));

const sourceCodes = (source = {}) =>
  Object.entries(source).map(([standard, code]) => h('span', { class: 'code' }, `${standard} ${code}`));

const renderTaxonomyNode = (t, node, depth = 0) => {
  const label = h('span', { class: 'node-label' },
    h('span', { class: 'level' }, t(`taxonomy.levels.${LEVELS[depth]}`)),
    h('span', {}, node.name),
    sourceCodes(node.source));
  const children = node.children ?? [];
  if (!children.length) return h('div', { class: 'node leaf' }, label);
  return h('details', { class: 'node' }, h('summary', {}, label),
    children.map((child) => renderTaxonomyNode(t, child, depth + 1)));
};

const renderTaxonomy = (t, taxonomy) =>
  taxonomy?.length ? taxonomy.map((node) => renderTaxonomyNode(t, node)) : [empty(t('taxonomy.empty'))];

const formatScore = (score) => (typeof score === 'number' ? score.toFixed(3) : '—');

const formatExternal = (external = []) =>
  external.length ? external.map(({ bench, score }) => `${bench}: ${formatScore(score)}`).join(' · ') : '—';

const renderExtensionTable = (t, items, withDelivery, emptyKey) => {
  if (!items?.length) return [empty(t(emptyKey))];
  const columns = ['name', 'category', ...(withDelivery ? ['delivery'] : []), 'bench', 'external'];
  const cells = (item) => [
    item.name,
    (item.primary ?? []).join(' › '),
    ...(withDelivery ? [(item.delivery ?? []).map((d) => t(`delivery.${d}`)).join(' + ')] : []),
    formatScore(item.bench),
    formatExternal(item.external),
  ];
  return [h('div', { class: 'table-wrap' }, h('table', {},
    h('thead', {}, h('tr', {}, columns.map((c) => h('th', {}, t(`columns.${c}`))))),
    h('tbody', {}, items.map((item) => h('tr', {}, cells(item).map((value) => h('td', {}, value)))))))];
};

const stat = (value, label) => h('div', { class: 'stat' }, h('strong', {}, String(value ?? 0)), h('span', {}, label));

const renderBenchmark = (t, benchmark = {}) => [
  stat(benchmark.samples, t('benchmark.samples')),
  stat(benchmark.categories, t('benchmark.categories')),
  ...REVIEWER_TITLES.map((title) => stat(benchmark.reviewers?.[title], t(`benchmark.reviewers.${title}`))),
];

const renderCitation = (t, citation) => (citation ? [h('pre', {}, citation)] : [empty(t('cite.empty'))]);

const fill = (id, nodes) => document.getElementById(id).replaceChildren(...nodes);

const render = (t, site) => {
  document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
  document.title = t('meta.title');
  fill('links', renderLinks(t, site.links));
  fill('taxonomy-levels', renderLevels(t));
  fill('taxonomy-tree', renderTaxonomy(t, site.taxonomy));
  fill('tools-table', renderExtensionTable(t, site.tools, true, 'tools.empty'));
  fill('skills-table', renderExtensionTable(t, site.skills, false, 'skills.empty'));
  fill('benchmark-stats', renderBenchmark(t, site.benchmark));
  fill('harness-base', [site.harness?.basedOn ? `${t('harness.basedOn')} ${site.harness.basedOn}` : t('harness.pending')]);
  fill('cite-body', renderCitation(t, site.citation));
};

const main = async () => {
  const [site, fallback] = await Promise.all([loadJson('data/site.json'), loadJson(`locales/${LOCALES.en}.json`)]);
  const toggle = document.getElementById('lang-toggle');

  const apply = async (requested) => {
    const dict = requested === 'en' ? fallback : await loadJson(`locales/${LOCALES[requested]}.json`);
    const lang = dict ? requested : 'en';
    const t = (key) => lookup(dict, key) ?? lookup(fallback, key) ?? key;
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
    toggle.textContent = lang === 'zh' ? 'EN' : '中文';
    toggle.onclick = () => { storage.set(LANG_KEY, lang === 'zh' ? 'en' : 'zh'); apply(lang === 'zh' ? 'en' : 'zh'); };
    render(t, site ?? {});
  };

  apply(initialLang());
};

main();
