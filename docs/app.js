import { $, esc, fail, int, kpis, legend, load, select, table, xy } from './kit.js';

const YEAR = 365.25 * 86400, yr = (t) => 1970 + t / YEAR;
const OUT = { fixed: ['fixed later', 'var(--c2)'], restored: ['the name came back', 'var(--c3)'], stale: ['still stale', 'var(--bad)'] };
try {
  const d = await load();
  const E = d.events, sections = E.flatMap((e) => e.stale.map((s) => ({ ...s, e, outcome: s.restored ? 'restored' : s.fixed ? 'fixed' : 'stale' })));
  const renames = E.flatMap((e) => e.renames || []);
  const fixedDays = sections.filter((s) => s.outcome === 'fixed').map((s) => s.days_later).sort((a, b) => a - b);
  const median = fixedDays.length ? fixedDays[Math.floor((fixedDays.length - 1) / 2)] : null;
  kpis($('#kpis'), [
    { label: 'Breaking changes the docs used', value: String(E.length), note: `in httpx's history up to ${d.pin.slice(0, 10)}` },
    { label: 'Documented in the same commit', value: String(E.filter((e) => !e.stale.length).length), note: `the other ${E.filter((e) => e.stale.length).length} left ${sections.length} sections stale` },
    { label: 'Median time a fixed section stayed wrong', value: `${Math.round(median)} days`, note: `${fixedDays.length} sections fixed later by hand` },
    { label: 'Rename fixes suggested', value: `${renames.filter((r) => r.suggested).length}/${renames.length}`, note: `${renames.filter((r) => r.matched).length} identical to the maintainers' own edit` },
  ]);
  $('#tlSub').textContent = `Each line is one doc section, from the commit that broke it to the commit that fixed it, or to the pinned commit (${new Date(d.pin_time * 1000).toISOString().slice(0, 10)}) if it is still wrong. The checker would have failed each of these pull requests on the day.`;
  const rows = [...sections].sort((a, b) => a.e.time - b.e.time);
  const end = (s) => (s.days_later != null ? s.e.time + s.days_later * 86400 : d.pin_time);
  const series = rows.map((s, i) => ({
    name: OUT[s.outcome][0], color: OUT[s.outcome][1], width: 5,
    points: [{ x: yr(s.e.time), y: rows.length - 1 - i }, { x: Math.max(yr(end(s)), yr(s.e.time) + 0.03), y: rows.length - 1 - i }],
  }));
  const dots = { name: 'break', line: false, dots: true, points: rows.map((s, i) => ({ x: yr(s.e.time), y: rows.length - 1 - i, r: 3.5, color: OUT[s.outcome][1], title: `${s.e.change.item} ${s.e.change.kind}: ${s.file} › ${s.section} (${OUT[s.outcome][0]}${s.days_later != null ? `, ${Math.round(s.days_later)} days` : ''})` })) };
  const y0 = Math.floor(yr(Math.min(...rows.map((s) => s.e.time)))), y1 = Math.ceil(yr(d.pin_time));
  xy($('#gantt'), { label: 'Doc sections stale over time', height: Math.max(240, rows.length * 13 + 60), series: [...series, dots],
    x: { min: y0, max: y1, fmt: (v) => String(Math.round(v)), ticks: Array.from({ length: y1 - y0 + 1 }, (_, i) => y0 + i) },
    y: { min: -1, max: rows.length, fmt: () => '', ticks: [] } });
  legend($('#ganttKey'), Object.values(OUT).map(([name, color]) => ({ name, color })));

  const outcome = (e) => (!e.stale.length ? 'same commit' : e.stale.every((s) => s.restored) ? 'name came back' : e.stale.some((s) => !s.fixed && !s.restored) ? 'still stale' : 'fixed later');
  const ev = E.map((e) => ({
    commit: `<a href="https://github.com/encode/httpx/commit/${esc(e.commit)}"><code>${esc(e.commit.slice(0, 8))}</code></a>`,
    date: new Date(e.time * 1000).toISOString().slice(0, 10),
    change: `<code>${esc(e.change.item)}</code> ${esc(e.change.kind)}${e.change.param ? ` <code>${esc(e.change.param)}</code>` : ''}${e.change.renamed_to ? ` → <code>${esc(e.change.renamed_to)}</code>` : ''}`,
    sections: e.stale.length ? e.stale.map((s) => `${esc(s.file)} › ${esc(s.section.split(' > ').slice(-1)[0])}${s.restored ? ' (name came back)' : s.fixed ? ` (fixed ${Math.round(s.days_later)} days later)` : ' <b class="err">(still stale)</b>'}`).join('<br>') : '<span class="muted">updated in the same commit</span>',
    outcome: outcome(e),
  }));
  const kinds = ['same commit', 'fixed later', 'name came back', 'still stale'];
  select($('#filter'), [['all', `all ${E.length}`], ...kinds.map((k) => [k, `${k} (${ev.filter((x) => x.outcome === k).length})`])], 'all', (k) => {
    table($('#events'), [
      { key: 'commit', label: 'Commit', html: true }, { key: 'date', label: 'Date' },
      { key: 'change', label: 'Change', html: true }, { key: 'sections', label: 'Doc sections left stale', html: true },
    ], k === 'all' ? ev : ev.filter((x) => x.outcome === k), { cls: (x) => (x.outcome === 'still stale' ? 'bad' : '') });
  });
  void int;
} catch (err) {
  fail(err);
}
