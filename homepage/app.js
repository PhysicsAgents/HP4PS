const LOCALES = { en: 'en_US', zh: 'zh_CN' };
const LANG_KEY = 'hp4ps.lang';
const LEVELS = ['domain', 'subfield', 'branch', 'researchPath', 'technicalPath'];
const LINKS = ['github', 'huggingface', 'arxiv', 'containers'];
const REVIEWER_TITLES = ['graduate', 'phd', 'professor'];

// Which list each catalog page shows, and the columns after name and category.
const CATALOGS = {
  skills: { items: (site) => site.skills, columns: ['bench', 'external'], emptyKey: 'skills.empty' },
  tools: { items: (site) => site.tools, columns: ['delivery', 'bench', 'external'], emptyKey: 'tools.empty' },
  benchmark: { items: (site) => site.samples, columns: [], emptyKey: 'benchmark.empty' },
};

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

// Taxonomy: nodes carry bilingual names and the codes of the standards they come from.
const indexTaxonomy = (nodes = []) => {
  const byId = new Map();
  const walk = (list, parent, depth) => list.forEach((node) => {
    byId.set(node.id, { node, parent, depth });
    walk(node.children ?? [], node, depth + 1);
  });
  walk(nodes, null, 0);
  return byId;
};

const ancestry = (index, id) => {
  const chain = [];
  for (let entry = index.get(id); entry; entry = entry.parent && index.get(entry.parent.id)) chain.unshift(entry.node);
  return chain;
};

const codeLabels = (source = {}) =>
  Object.entries(source).map(([standard, code]) => `${standard === 'GB' ? 'GB/T' : standard} ${[code].flat().join(', ')}`);

const sourceCodes = (source) => codeLabels(source).map((label) => h('span', { class: 'code' }, label));

const renderLinks = (t, links) =>
  LINKS.map((name) =>
    links?.[name]
      ? h('a', { class: 'button', href: links[name], rel: 'noopener' }, t(`links.${name}`))
      : h('span', { class: 'button disabled', title: t('links.pending') }, t(`links.${name}`)));

// Text in site.json may be a plain string or { en, zh }.
const pick = (ctx, value) => (value && typeof value === 'object' ? value[ctx.lang] ?? value.en : value);

// Home: horizontally scrolling card rows ("carousels") with prev/next buttons.
const COVERAGE_TABS = ['skills', 'tools', 'benchmark'];
const PLACEHOLDER_CARDS = 3;
const PLACEHOLDER_LOGOS = 6;

const setupCarousel = (id) => {
  const track = document.getElementById(`${id}-track`);
  document.querySelectorAll(`[data-carousel="${id}"]`).forEach((button) => {
    button.onclick = () => track.scrollBy({ left: Number(button.dataset.step) * track.clientWidth * 0.9, behavior: 'smooth' });
  });
};

const coverageCards = (ctx, tab) => {
  const items = CATALOGS[tab].items(ctx.site) ?? [];
  const page = tab === 'benchmark' ? 'benchmark.html' : `${tab}.html`;
  const domains = (ctx.taxonomy.nodes ?? []).map((domain) => {
    const inDomain = items.filter((item) => inCategory(item, domain.id));
    const subfields = new Set(inDomain.map((item) => item.category?.[1]).filter(Boolean));
    return { domain, count: inDomain.length, subfields: subfields.size };
  }).sort((a, b) => b.count - a.count);
  const covered = domains.filter((d) => d.count);
  fill('coverage-summary', [ctx.t('coverage.summary')
    .replace('{items}', items.length)
    .replace('{domains}', covered.length)
    .replace('{subfields}', covered.reduce((sum, d) => sum + d.subfields, 0))]);
  return domains.map(({ domain, count, subfields }) => h('a', { class: `slide coverage-card${count ? '' : ' is-empty'}`, href: `${page}#c=${domain.id}` },
    h('span', { class: 'slide-kicker' }, `PACS ${domain.source.PACS}`),
    h('h3', {}, ctx.name(domain)),
    h('div', { class: 'slide-figure' }, h('strong', {}, String(count)), h('span', {}, ctx.t(`coverage.unit.${tab}`))),
    h('span', { class: 'slide-meta' }, ctx.t('coverage.subfields').replace('{n}', subfields))));
};

const renderCoverage = (ctx) => {
  const tabs = COVERAGE_TABS.map((tab) => {
    const button = h('button', { class: 'tab', type: 'button', role: 'tab', 'aria-selected': String(tab === ctx.coverageTab) }, ctx.t(`nav.${tab}`));
    button.onclick = () => { ctx.coverageTab = tab; renderCoverage(ctx); };
    return button;
  });
  fill('coverage-tabs', tabs);
  fill('coverage-track', coverageCards(ctx, ctx.coverageTab));
  document.getElementById('coverage-track').scrollLeft = 0;
};

const renderResults = (ctx) => {
  const results = ctx.site.results ?? [];
  fill('results-track', results.length
    ? results.map((result) => h(result.link ? 'a' : 'article', { class: 'slide result-card', ...(result.link ? { href: result.link, rel: 'noopener' } : {}) },
      h('span', { class: 'slide-kicker' }, pick(ctx, result.field) ?? ''),
      h('h3', {}, pick(ctx, result.title)),
      result.metric ? h('div', { class: 'slide-figure' }, h('strong', {}, pick(ctx, result.metric))) : null,
      h('p', {}, pick(ctx, result.summary) ?? '')))
    : Array.from({ length: PLACEHOLDER_CARDS }, () => h('article', { class: 'slide result-card placeholder' },
      h('span', { class: 'slide-kicker' }, ctx.t('results.pending')),
      h('h3', {}, ctx.t('results.placeholder')))));
};

const renderPartners = (ctx) => {
  const partners = ctx.site.partners ?? [];
  fill('partners-wall', partners.length
    ? partners.map((partner) => h(partner.url ? 'a' : 'div', { class: 'logo', title: pick(ctx, partner.name), ...(partner.url ? { href: partner.url, rel: 'noopener' } : {}) },
      partner.logo ? h('img', { src: partner.logo, alt: pick(ctx, partner.name), loading: 'lazy' }) : h('span', {}, pick(ctx, partner.name))))
    : Array.from({ length: PLACEHOLDER_LOGOS }, () => h('div', { class: 'logo placeholder' }, h('span', {}, ctx.t('partners.placeholder')))));
};

const formatScore = (score) => (typeof score === 'number' ? score.toFixed(3) : '—');

const formatExternal = (external = []) =>
  external.length ? external.map(({ bench, score }) => `${bench}: ${formatScore(score)}`).join(' · ') : '—';

// The deepest category links to its place in the sidebar; the full chain shows on hover.
const categoryCell = (ctx, ids = []) => {
  const last = ids[ids.length - 1];
  if (!last || !ctx.index.has(last)) return '—';
  const chain = ancestry(ctx.index, last);
  return h('a', { href: categoryHref(last), title: chain.map(ctx.name).join(' › ') }, ctx.name(chain[chain.length - 1]));
};

const renderTable = (ctx, items, extraColumns) => {
  const columns = ['name', 'category', 'researchPath', 'technicalPath', ...extraColumns];
  const value = (item, column) => ({
    name: item.name,
    category: categoryCell(ctx, item.category),
    researchPath: item.researchPath ?? '—',
    technicalPath: item.technicalPath ?? '—',
    delivery: (item.delivery ?? []).map((d) => ctx.t(`delivery.${d}`)).join(' + ') || '—',
    bench: formatScore(item.bench),
    external: formatExternal(item.external),
  })[column];
  return h('div', { class: 'table-wrap' }, h('table', {},
    h('thead', {}, h('tr', {}, columns.map((c) => h('th', {}, ctx.t(`columns.${c}`))))),
    h('tbody', {}, items.map((item) => h('tr', {}, columns.map((c) => h('td', {}, value(item, c))))))));
};

const stat = (value, label) => h('div', { class: 'stat' }, h('strong', {}, String(value ?? 0)), h('span', {}, label));

const renderBenchmark = (t, benchmark = {}) => [
  stat(benchmark.samples, t('benchmark.samples')),
  stat(benchmark.categories, t('benchmark.categories')),
  ...REVIEWER_TITLES.map((title) => stat(benchmark.reviewers?.[title], t(`benchmark.reviewers.${title}`))),
];

const fill = (id, nodes) => document.getElementById(id)?.replaceChildren(...nodes);

// Catalog pages: sidebar tree of categories, list filtered by the selected one.
const selectedCategory = () => new URLSearchParams(location.hash.slice(1)).get('c');
const categoryHref = (id) => (id ? `#c=${encodeURIComponent(id)}` : '#');

const inCategory = (item, id) =>
  [item.category, ...(item.related ?? [])].some((path) => Array.isArray(path) && path.includes(id));

const matchesFilter = (ctx, node, query) =>
  !query || `${ctx.name(node)} ${Object.values(node.source ?? {}).join(' ')}`.toLowerCase().includes(query);

const visibleIds = (ctx, query) => {
  if (!query) return null;
  const keep = new Set();
  ctx.index.forEach(({ node }, id) => {
    if (matchesFilter(ctx, node, query)) ancestry(ctx.index, id).forEach((a) => keep.add(a.id));
  });
  return keep;
};

const renderTree = (ctx, items, query) => {
  const selected = selectedCategory();
  const open = new Set(selected ? ancestry(ctx.index, selected).map((n) => n.id) : []);
  const keep = visibleIds(ctx, query);
  const count = (id) => items.filter((item) => inCategory(item, id)).length;

  const branch = (nodes, depth) => h('ul', { class: `tree-level depth-${depth}` }, nodes
    .filter((node) => !keep || keep.has(node.id))
    .map((node) => {
      const children = node.children ?? [];
      const expanded = Boolean(keep) || open.has(node.id) || ctx.expanded.has(node.id);
      const toggle = children.length
        ? h('button', { class: 'tree-toggle', type: 'button', 'aria-expanded': String(expanded), 'aria-label': ctx.name(node) })
        : h('span', { class: 'tree-toggle placeholder' });
      toggle.onclick = () => {
        if (ctx.expanded.has(node.id)) ctx.expanded.delete(node.id); else ctx.expanded.add(node.id);
        ctx.renderTree();
      };
      const codes = codeLabels(node.source).join(' · ');
      const link = h('a', {
        class: 'tree-link', href: categoryHref(node.id), title: codes,
        ...(node.id === selected ? { 'aria-current': 'true' } : {}),
      }, h('span', { class: 'tree-name' }, ctx.name(node)), h('span', { class: 'tree-count' }, String(count(node.id))));
      return h('li', {}, h('div', { class: 'tree-row' }, toggle, link),
        children.length && expanded ? branch(children, depth + 1) : null);
    }));

  const all = h('a', { class: 'tree-link tree-all', href: categoryHref(null), ...(selected ? {} : { 'aria-current': 'true' }) },
    h('span', { class: 'tree-name' }, ctx.t('catalog.all')), h('span', { class: 'tree-count' }, String(items.length)));
  const tree = branch(ctx.taxonomy.nodes ?? [], 0);
  return [all, tree.children.length ? tree : empty(ctx.t('catalog.noMatch'))];
};

const renderCatalog = (ctx, config) => {
  const items = config.items(ctx.site) ?? [];
  const selected = selectedCategory();
  const chain = selected && ctx.index.has(selected) ? ancestry(ctx.index, selected) : [];
  const filter = document.getElementById('tree-filter');

  ctx.renderTree = () => fill('tree', renderTree(ctx, items, filter.value.trim().toLowerCase()));
  filter.oninput = ctx.renderTree;
  ctx.renderTree();

  fill('crumbs', [
    h('a', { href: categoryHref(null) }, ctx.t('catalog.all')),
    ...chain.map((node) => [h('span', { class: 'sep' }, '›'), h('a', { href: categoryHref(node.id) }, ctx.name(node))]),
  ].flat());

  const current = chain[chain.length - 1];
  fill('category-card', current ? [h('div', { class: 'category-card' },
    h('span', { class: 'level' }, ctx.t(`taxonomy.levels.${LEVELS[chain.length - 1]}`)),
    h('h2', {}, ctx.name(current)),
    h('div', { class: 'codes' }, sourceCodes(current.source)))] : []);

  const shown = current ? items.filter((item) => inCategory(item, current.id)) : items;
  fill('catalog', shown.length
    ? [renderTable(ctx, shown, config.columns)]
    : [empty(ctx.t(items.length ? 'catalog.emptyCategory' : config.emptyKey))]);
};

const setupDrawer = () => {
  const toggle = document.getElementById('sidebar-toggle');
  if (!toggle) return;
  const close = () => document.body.classList.remove('nav-open');
  toggle.onclick = () => document.body.classList.toggle('nav-open');
  document.getElementById('backdrop').onclick = close;
  document.getElementById('sidebar').addEventListener('click', (event) => {
    if (event.target.closest('.tree-link')) close();
  });
};

const page = document.body.dataset.page;

const render = (ctx) => {
  const { t, site } = ctx;
  document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  document.querySelectorAll('[data-i18n-label]').forEach((el) => el.setAttribute('aria-label', t(el.dataset.i18nLabel)));
  document.title = page === 'home' ? t('meta.title') : `${t(`nav.${page}`)} · HP4PS`;
  fill('links', renderLinks(t, site.links));
  fill('benchmark-stats', renderBenchmark(t, site.benchmark));
  if (page === 'home') {
    renderCoverage(ctx);
    renderResults(ctx);
    renderPartners(ctx);
  }
  if (CATALOGS[page]) renderCatalog(ctx, CATALOGS[page]);
};

document.querySelectorAll(`.topbar [data-page="${page}"]`).forEach((link) => link.setAttribute('aria-current', 'page'));

const main = async () => {
  const [site, taxonomy, fallback] = await Promise.all([
    loadJson('data/site.json'), loadJson('data/taxonomy.json'), loadJson(`locales/${LOCALES.en}.json`),
  ]);
  const toggle = document.getElementById('lang-toggle');
  const index = indexTaxonomy(taxonomy?.nodes);
  const expanded = new Set();
  let current = null;

  const apply = async (requested) => {
    const dict = requested === 'en' ? fallback : await loadJson(`locales/${LOCALES[requested]}.json`);
    const lang = dict ? requested : 'en';
    const t = (key) => lookup(dict, key) ?? lookup(fallback, key) ?? key;
    const name = (node) => node.name?.[lang] ?? node.name?.en ?? node.id;
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
    toggle.textContent = lang === 'zh' ? 'EN' : '中文';
    toggle.onclick = () => { storage.set(LANG_KEY, lang === 'zh' ? 'en' : 'zh'); apply(lang === 'zh' ? 'en' : 'zh'); };
    current = { t, name, lang, site: site ?? {}, taxonomy: taxonomy ?? {}, index, expanded, coverageTab: current?.coverageTab ?? 'skills' };
    render(current);
  };

  setupDrawer();
  ['coverage', 'results'].forEach(setupCarousel);
  window.addEventListener('hashchange', () => current && render(current));
  apply(initialLang());
};

main();
