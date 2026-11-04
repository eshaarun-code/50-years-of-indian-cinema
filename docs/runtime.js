// Stands in for the Claude dashboard runtime so the page runs as a plain static site.
// Same calls the page already makes: dash.calc, dash.draw, dash.data, dash.params, dash.setParams, dash.onData.
(() => {
  const calcs = {}, draws = {}, listeners = [], results = {};
  const sources = { films: 'data/films.json', directors: 'data/directors.json' };
  let params = { scope: 'all', director: 'S.S. Rajamouli' };
  let state = 'loading';

  const rows = (id) => {
    if (id in results) return results[id];
    const c = calcs[id];
    results[id] = c.fn(...c.inputs.map(rows));
    return results[id];
  };

  const drawOne = (name) => {
    document.querySelectorAll(`[data-draw="${name}"]`).forEach((el) => {
      try { draws[name](el); } catch (err) { console.error('draw failed: ' + name, err); }
      el.classList.remove('dash-skeleton');
    });
  };
  const render = () => {
    Object.keys(draws).forEach(drawOne);
    listeners.forEach((fn) => fn());
  };

  window.dash = {
    calc: (id, def) => { calcs[id] = def; },
    draw: (name, fn) => { if (fn) draws[name] = fn; else drawOne(name); },
    data: (id) => (state === 'ok' ? { status: 'ok', data: rows(id) } : { status: state, data: [] }),
    params: () => params,
    setParams: (patch) => {
      params = { ...params, ...patch };
      Object.keys(params).forEach((k) => { if (params[k] == null) delete params[k]; });
      render();
    },
    onData: (fn) => { listeners.push(fn); },
  };

  // charts size themselves to their box, so redraw when the box changes
  let width = 0, timer;
  new ResizeObserver(() => {
    const w = document.documentElement.clientWidth;
    if (w === width) return;
    const first = !width;
    width = w;
    if (first) return;
    clearTimeout(timer);
    timer = setTimeout(render, 150);
  }).observe(document.documentElement);
  document.addEventListener('toggle', (e) => { if (e.target.open) render(); }, true);

  const load = async () => {
    const names = Object.keys(sources);
    try {
      const got = await Promise.all(names.map((n) => fetch(sources[n]).then((r) => {
        if (!r.ok) throw new Error(sources[n] + ' ' + r.status);
        return r.json();
      })));
      names.forEach((n, i) => { results[n] = got[i]; });
      state = 'ok';
    } catch (err) {
      console.error('data failed to load', err);
      state = 'error';
    }
    render();
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load);
  else load();
})();
