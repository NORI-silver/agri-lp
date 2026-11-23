'use strict';

window.AgriMatching = {
  async render({ main }) {
    const route = location.pathname.split('/').filter(Boolean);
    const page = route[0] || 'home';
    const pages = ['home', 'match', 'producers', 'compare', 'inquiry', 'requests', 'for-producers', 'how-it-works'];
    const active = pages.includes(page) && !(page === 'producers' && route[1]);
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    const icons = {
      home: '<path d="m3 10 9-7 9 7v10H3z"/><path d="M9 20v-7h6v7"/>',
      search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
      compare: '<rect x="3" y="4" width="7" height="16" rx="1"/><rect x="14" y="4" width="7" height="16" rx="1"/><path d="M6 9h1m-1 4h1m10-4h1m-1 4h1"/>',
      saved: '<path d="M6 3h12v18l-6-4-6 4z"/>',
      close: '<path d="m6 6 12 12M18 6 6 18"/>',
      check: '<path d="m5 12 4 4L19 6"/>',
      leaf: '<path d="M20 3C8 2 2 10 6 17 13 21 22 15 20 3Z"/><path d="m4 21 12-12"/>',
      shop: '<path d="M3 9h18l-2-6H5zM5 9v12h14V9M9 21v-7h6v7"/>',
      external: '<path d="M14 3h7v7m0-7-11 11M10 4H4v16h16v-6"/>',
      file: '<path d="M5 3h9l5 5v13H5zM14 3v6h5M8 13h8m-8 4h5"/>',
      location: '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 0 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
    };
    const icon = name => `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.leaf}</svg>`;
    const toast = message => {
      const target = document.querySelector('#global-status');
      target.textContent = message;
      target.classList.add('visible');
      clearTimeout(window.agriToastTimer);
      window.agriToastTimer = setTimeout(() => target.classList.remove('visible'), 4500);
    };
    const menuButton = document.querySelector('#menu-toggle');
    const menu = document.querySelector('#site-menu');
    const closeMenu = () => { menuButton?.setAttribute('aria-expanded', 'false'); menu?.classList.remove('open'); };
    if (menuButton) {
      menuButton.onclick = () => {
        const open = menuButton.getAttribute('aria-expanded') !== 'true';
        menuButton.setAttribute('aria-expanded', String(open));
        menu.classList.toggle('open', open);
      };
      menu.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
      document.addEventListener('keydown', e => { if (e.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') { closeMenu(); menuButton.focus(); } });
    }
    document.querySelectorAll('[data-mobile]').forEach(a => {
      a.querySelector('span').innerHTML = icon(a.dataset.mobile);
      const selected = (page === 'home' && a.dataset.mobile === 'home') || (['producers', 'match'].includes(page) && a.dataset.mobile === 'search') || (['compare', 'inquiry'].includes(page) && a.dataset.mobile === 'compare') || (page === 'requests' && a.dataset.mobile === 'saved');
      if (selected) a.setAttribute('aria-current', 'page');
    });
    try {
      const cart = JSON.parse(localStorage.getItem('agri-demo-v1'))?.cart || {};
      document.querySelector('#count').textContent = Object.values(cart).filter(n => Number.isInteger(n) && n > 0).reduce((a, b) => a + b, 0);
    } catch {}
    if (!active) return false;

    const core = window.AgriMatchCore;
    const key = 'agri-matching-v1';
    let state = { request: {}, selected: [], drafts: [] };
    try {
      const stored = JSON.parse(localStorage.getItem(key));
      if (stored && stored.request && !Array.isArray(stored.request) && Array.isArray(stored.selected) && Array.isArray(stored.drafts)) state = stored;
    } catch {}
    let refs;
    try {
      const response = await fetch('/shop/references.json');
      if (!response.ok) throw Error();
      refs = await response.json();
    } catch {
      main.innerHTML = `<div class="page-shell empty-state"><h1>情報を読み込めませんでした</h1><p>通信状況を確認し、もう一度お試しください。</p><button onclick="location.reload()">再読み込みする</button></div>`;
      return true;
    }
    state.selected = [...new Set(state.selected)].filter(id => refs.some(r => r.id === id)).slice(0, 3);
    state.drafts = state.drafts.filter(d => d && typeof d.id === 'string' && typeof d.text === 'string').slice(0, 20);
    const persist = () => {
      try { localStorage.setItem(key, JSON.stringify(state)); return true; }
      catch { toast('端末に保存できません。相談文はコピーかダウンロードをご利用ください。'); return false; }
    };
    const selectedRefs = () => refs.filter(r => state.selected.includes(r.id));
    const categories = [
      { name: '野菜', sub: '旬の彩りを、毎日の食卓に。', image: 'harvest-hero.webp', position: '70% 70%' },
      { name: '果物', sub: '季節のおいしさを探す。', image: 'fruit-editorial.webp' },
      { name: '米', sub: 'いつもの一膳から、こだわる。', image: 'rice-editorial.webp' },
      { name: 'その他', sub: '加工品など、農の楽しみ。', image: 'pantry-editorial.webp' },
    ];
    const purposeName = value => value === 'household' ? '家庭用' : value === 'business' ? '飲食店・事業者' : value;
    const purposeParam = value => value === '家庭用' ? 'household' : value === '飲食店・事業者' ? 'business' : value;
    const image = (file, alt, extra = '') => `<img src="/shop/images/${file}" alt="${esc(alt)}" width="720" height="480" loading="lazy" ${extra}>`;
    const provenance = '<p class="provenance">公式サイトの公開情報を参照しています。提携・登録生産者の一覧ではなく、現在の受付可否は各窓口でご確認ください。</p>';
    const steps = current => `<nav class="journey" aria-label="相談までの流れ">${['探す', '比較する', '相談文をつくる'].map((text, i) => `<span ${i === current ? 'aria-current="step"' : ''}>${text}</span>`).join('')}</nav>`;
    const displayedLocation = r => r.locality && !r.locality.includes(r.region) ? r.region + r.locality : r.locality || r.region;
    const criteria = r => [r.audiences.includes('家庭用') ? '家庭向けの案内' : (r.audiences.includes('飲食店・事業者') ? '事業者向けの案内' : ''), r.smallLot === true ? '小口相談の案内' : '', r.frequency.includes('定期') ? '定期・継続の案内' : ''].filter(Boolean);
    const mini = r => r.photo ? `<span class="farm-monogram farm-profile-wrap" aria-hidden="true"><img class="farm-profile-photo" src="${esc(r.photo)}" alt="" width="120" height="120" loading="lazy"></span>` : `<span class="farm-monogram farm-${r.id}" aria-hidden="true">${esc(r.name.slice(0, 1))}</span>`;
    const card = (r, evaluation) => `<article class="farm-card reference-card" data-ref="${r.id}">
      <div class="farm-card-top">${mini(r)}<span class="farm-location">${icon('location')}${esc(displayedLocation(r))}</span><button class="select-farm ${state.selected.includes(r.id) ? 'selected' : ''}" data-select="${r.id}" type="button" aria-pressed="${state.selected.includes(r.id)}" aria-label="${esc(r.name)}を比較${state.selected.includes(r.id) ? 'から外す' : 'に追加'}">${icon(state.selected.includes(r.id) ? 'check' : 'compare')}<span>${state.selected.includes(r.id) ? '選択中' : '比較'}</span></button></div>
      <p class="farm-crops">${esc(r.commodities || r.categories.join(' / '))}</p><h3>${esc(r.name)}</h3>${r.summary ? `<p class="farm-summary">${esc(r.summary)}</p>` : ''}
      <div class="farm-tags">${criteria(r).map(t => `<span>${esc(t)}</span>`).join('')}</div>
      ${evaluation?.unknown.length > 1 ? `<p class="condition-note">数量・納品など、個別の条件は相談時に確認</p>` : ''}
      <div class="farm-card-bottom"><button type="button" class="text-button" data-detail="${r.id}">公開されている案内を見る</button><span class="source-label">${esc(r.sourcePlatform || '公式情報')}</span></div>
    </article>`;

    function updateSelection() {
      document.querySelectorAll('[data-selected-count]').forEach(el => { el.textContent = state.selected.length; });
      main.querySelectorAll('[data-select]').forEach(button => {
        const selected = state.selected.includes(button.dataset.select);
        const ref = refs.find(r => r.id === button.dataset.select);
        button.setAttribute('aria-pressed', String(selected));
        button.setAttribute('aria-label', `${ref.name}を比較${selected ? 'から外す' : 'に追加'}`);
        button.classList.toggle('selected', selected);
        button.innerHTML = icon(selected ? 'check' : 'compare') + `<span>${selected ? '選択中' : '比較'}</span>`;
      });
      let bar = document.querySelector('#selection-bar');
      if (!bar) { bar = document.createElement('aside'); bar.id = 'selection-bar'; bar.className = 'selection-bar'; bar.setAttribute('aria-label', '選択した相談先'); document.body.append(bar); }
      const show = state.selected.length && !['compare', 'inquiry'].includes(page);
      bar.hidden = !show;
      document.body.classList.toggle('has-selection', !!show);
      if (show) {
        bar.innerHTML = `<div class="selection-farms">${selectedRefs().map(mini).join('')}<p><strong>${state.selected.length}件</strong><span>比較に追加しました</span></p></div><button class="text-button selection-reset" id="reset-selection">選択を解除</button><a class="button" href="/compare/">比較する</a>`;
        document.querySelector('#reset-selection').onclick = () => { state.selected = []; persist(); updateSelection(); };
      }
    }
    function select(id) {
      if (state.selected.includes(id)) state.selected = state.selected.filter(x => x !== id);
      else if (state.selected.length < 3) state.selected.push(id);
      else { toast('比較できるのは3件までです。選択を外してから追加してください。'); return; }
      persist(); updateSelection();
    }
    function bindCards(container = main) {
      container.querySelectorAll('[data-select]').forEach(button => { button.onclick = () => select(button.dataset.select); });
      container.querySelectorAll('[data-detail]').forEach(button => { button.onclick = () => openDetail(button.dataset.detail); });
    }
    function openDetail(id) {
      const r = refs.find(r => r.id === id);
      let dialog = document.querySelector('#farm-dialog');
      if (!dialog) { dialog = document.createElement('dialog'); dialog.id = 'farm-dialog'; dialog.className = 'farm-dialog'; document.body.append(dialog); }
      dialog.setAttribute('aria-labelledby', 'farm-dialog-title');
      dialog.innerHTML = `<div class="dialog-head"><span>生産者の公式情報</span><button type="button" class="icon-button" id="close-dialog" aria-label="詳細を閉じる">${icon('close')}</button></div><div class="dialog-content"><div class="detail-farm">${mini(r)}<div><p>${esc(displayedLocation(r))}${r.categories.length ? ` / ${r.categories.map(esc).join('・')}` : ''}</p><h2 id="farm-dialog-title">${esc(r.name)}</h2></div></div>${r.summary ? `<p>${esc(r.summary)}</p>` : ''}${r.evidence.length ? `<h3>${r.sourcePlatform ? '産地・品目' : '公式サイトの案内'}</h3><ul class="evidence-list">${r.evidence.map(e => `<li>${icon('check')}<span>${esc(e.text)}</span></li>`).join('')}</ul>` : ''}<div class="confirm-box"><h3>相談するときに確認したいこと</h3><p>希望品目の収穫・在庫、必要な数量、納品日と配送先、見積りと支払条件。現在の受付可否は未確認です。</p></div>${r.photo ? '<p class="source-date">プロフィール写真：食べチョク掲載画像</p>' : ''}${r.checked ? `<p class="source-date">公開情報の確認日：${esc(r.checked)}</p>` : ''}${r.profileSource && r.profileSource !== r.url ? `<p><a href="${esc(r.profileSource)}" target="_blank" rel="noopener noreferrer">紹介の出典</a></p>` : ''}<a class="external-link" href="${esc(r.url)}" target="_blank" rel="noopener noreferrer" data-inquiry="producer-official">${r.sourcePlatform ? '食べチョクのプロフィールを開く' : '出典の公式サイトを開く'} ${icon('external')}</a>${provenance}</div><div class="dialog-actions"><button id="dialog-select" class="${state.selected.includes(id) ? 'secondary' : ''}">${state.selected.includes(id) ? '比較から外す' : '比較に追加する'}</button><a href="/match/" class="text-button">希望条件を整理する</a></div>`;
      document.querySelector('#close-dialog').onclick = () => dialog.close();
      document.querySelector('#dialog-select').onclick = () => { select(id); dialog.close(); };
      dialog.onclick = e => { if (e.target === dialog) { const box = dialog.getBoundingClientRect(); if (e.clientX < box.left || e.clientX > box.right || e.clientY < box.top || e.clientY > box.bottom) dialog.close(); } };
      dialog.showModal();
    }
    const intro = (eyebrow, title, text) => `<div class="page-intro"><p class="eyebrow">${eyebrow}</p><h1>${title}</h1>${text ? `<p class="page-lead">${text}</p>` : ''}</div>`;
    function emptySelection() {
      main.innerHTML = `<div class="page-shell">${steps(1)}<div class="empty-state">${icon('compare')}<h1>気になる相談先を、比較に追加しよう。</h1><p>候補の比較ボタンで、最大3件まで追加できます。</p><a class="button" href="/producers/">生産者の情報から探す</a><a class="text-button" href="/match/">希望条件から探す</a></div></div>`;
    }
    function evaluate(request) {
      const list = refs.map(r => core.evaluate(r, request));
      const known = e => (!request.category || e.results.some(c => c.field === 'category' && c.state === 'published')) && (!request.audience || e.results.some(c => c.field === 'audience' && c.state === 'published')) && !e.excluded;
      return { published: list.filter(known), unknown: list.filter(e => !known(e) && !e.excluded), excluded: list.filter(e => e.excluded) };
    }
    function resultHTML(request) {
      const list = evaluate(request);
      return `<div class="results-heading"><div><p class="eyebrow">希望する用途・品目の案内</p><h2>相談先の候補 <span>${list.published.length}件</span></h2></div><p>順位を付けず、掲載順で表示しています</p></div>${list.published.length ? `<div class="farm-grid">${list.published.map(e => card(e.ref, e)).join('')}</div>` : '<div class="empty-results"><h3>この用途・品目の案内は、まだ見つかっていません。</h3><p>条件を変えるか、公開条件が未確認の情報をご覧ください。<br>取引に対応できないという意味ではありません。</p></div>'}${list.unknown.length ? `<details class="unknown-results"><summary>用途・品目の対応が未確認の情報も見る <span>${list.unknown.length}件</span></summary><p>該当条件の案内を確認できていない参照先です。非対応とは断定していません。</p><div class="farm-grid">${list.unknown.map(e => card(e.ref, e)).join('')}</div></details>` : ''}${provenance}`;
    }
    function prefill(form, request) {
      for (const [name, value] of Object.entries(request)) {
        const field = form.elements.namedItem(name);
        if (!field) continue;
        if (field.type === 'checkbox') field.checked = !!value;
        else field.value = String(value);
      }
    }
    function readRequest(form) {
      const values = new FormData(form), request = {};
      for (const field of Object.keys(core.fields)) {
        const value = values.get(field);
        if (value) request[field] = field === 'smallLot' ? true : String(value).trim();
      }
      return request;
    }

    if (page === 'home') {
      main.dataset.page = 'home';
      main.innerHTML = `<section class="home-hero"><img class="hero-photograph" src="/shop/images/harvest-hero.webp" alt="畑で収穫した野菜を表したイメージ" width="1536" height="1024" fetchpriority="high"><div class="hero-shade"></div><div class="hero-copy"><p class="eyebrow">生産者と、いい出会いを。</p><h1>食べたいものから、<br>つくる人と<br>つながろう。</h1><p>家庭のお取り寄せも、お店の仕入れも。<br>品目や取引の希望から、相談先を探せます。</p><a class="hero-link" href="/match/">希望条件を整理して探す</a></div><span class="image-credit">AI生成のイメージ写真</span></section>
      <div class="home-search-wrap"><form id="home-search" class="home-search" action="/producers/"><label class="search-purpose"><span>何に使いますか</span><select name="audience"><option value="">用途を選ぶ</option><option value="household">家庭で楽しむ</option><option value="business">お店・事業で使う</option></select></label><label class="search-keyword"><span>どんな農産物を探しますか</span><input name="q" type="search" maxlength="100" placeholder="野菜、米、農園名など"></label><button type="submit">${icon('search')}探す</button></form><p class="search-support">公式情報を比較して、相談文まで準備できます。相談は各生産者の公式窓口へ。</p></div>
      <section class="home-section"><div class="section-heading"><div><p class="eyebrow">いつもの食卓にも、こだわりの一皿にも。</p><h2>食材から探す</h2></div><a href="/producers/">すべての情報を見る</a></div><div class="category-grid">${categories.map(c => `<a class="category-card" href="/producers/?category=${encodeURIComponent(c.name)}">${image(c.image, `${c.name}のイメージ`, c.position ? `style="object-position:${c.position}"` : '')}<div><h3>${c.name}</h3><p>${c.sub}</p></div></a>`).join('')}</div><p class="image-note">カテゴリー写真はAI生成のイメージです。実在の農園・商品を撮影したものではありません。</p></section>
      <section class="purpose-section"><div class="purpose-copy"><p class="eyebrow">選び方は、ひとつじゃない。</p><h2>あなたに合う<br>つながり方を。</h2><p>「少しずつ楽しみたい」も、<br>「毎週、届けてほしい」も。</p></div><div class="purpose-options"><a href="/match/?audience=household">${icon('home')}<div><h3>家庭で、旬を楽しむ</h3><p>少量・定期便・食べきれる量。<br>暮らしに合う希望を整理します。</p></div><span class="purpose-action">家庭用で探す</span></a><a href="/match/?audience=business">${icon('shop')}<div><h3>お店の、仕入れ先を探す</h3><p>数量・規格・納品頻度。<br>取引に必要な条件をまとめます。</p></div><span class="purpose-action">事業用で探す</span></a></div></section>
      <section class="home-section"><div class="section-heading"><div><p class="eyebrow">相談のきっかけを見つけよう。</p><h2>生産者の公式情報</h2></div><a href="/producers/">相談先を探す</a></div><div class="farm-grid home-farms">${refs.filter(r => ['nishikaze', 'kinameru', 'chiba'].includes(r.id)).map(r => card(r)).join('')}</div>${provenance}</section>
      <section class="guide-strip"><div><p class="eyebrow">はじめての方へ</p><h2>いい出会いは、<br>希望を伝えることから。</h2></div><div class="guide-flow"><article><span>探す</span><p>品目や用途から、<br>相談先の情報を見つける。</p></article><article><span>比べる</span><p>公開されている条件と、<br>確認が必要なことを知る。</p></article><article><span>相談する</span><p>相談文を準備して、<br>公式窓口へ持っていく。</p></article></div><a class="button secondary" href="/how-it-works/">ご利用ガイドを見る</a></section>`;
      bindCards();
    } else if (page === 'producers') {
      main.dataset.page = 'producers';
      const params = new URLSearchParams(location.search);
      main.innerHTML = `<div class="page-shell">${intro('FIND YOUR CONNECTION', '生産者の相談先を探す', '農産物、用途、産地から。気になる情報を比較に追加してみましょう。')}<form id="directory-search" class="directory-search"><label class="directory-query">${icon('search')}<span class="sr-only">キーワード</span><input name="q" id="reference-search" type="search" maxlength="100" placeholder="農産物・農園名・地域を入力"></label><button>検索する</button><div class="directory-filters"><label>用途<select name="audience"><option value="">すべての用途</option><option value="household">家庭用</option><option value="business">飲食店・事業者</option></select></label><label>農園の所在地<select name="region"><option value="">すべての地域</option>${[...new Set(refs.map(r => r.region))].map(r => `<option>${esc(r)}</option>`).join('')}</select></label><button type="button" id="reset-filters" class="text-button">条件をリセット</button></div><fieldset class="category-chips"><legend class="sr-only">品目の分類</legend>${['すべて', ...categories.map(c => c.name)].map((c, i) => `<label><input type="radio" name="category" value="${i ? c : ''}" ${!i ? 'checked' : ''}><span>${c}</span></label>`).join('')}</fieldset></form><div id="directory-results" aria-live="polite"></div></div>`;
      const form = document.querySelector('#directory-search');
      prefill(form, Object.fromEntries(params));
      let visible = 24;
      const run = (replaceURL = true, keepPage = false) => {
        if (!keepPage) visible = 24;
        const values = new FormData(form), q = String(values.get('q') || '').normalize('NFKC').toLowerCase().trim();
        const request = { category: String(values.get('category') || ''), audience: purposeName(String(values.get('audience') || '')) };
        state.request = { ...state.request, category: request.category, audience: request.audience }; persist();
        const filtered = refs.filter(r => (!values.get('region') || r.region === values.get('region')) && (r.name + r.region + (r.locality || '') + (r.summary || '') + (r.commodities || '') + r.categories.join('')).normalize('NFKC').toLowerCase().includes(q));
        const evaluated = evaluate(request);
        const eligible = evaluated.published.filter(e => filtered.includes(e.ref));
        const unknown = evaluated.unknown.filter(e => filtered.includes(e.ref));
        document.querySelector('#directory-results').innerHTML = `<div class="results-heading"><h2>公開情報 <span id="reference-count">${eligible.length}件</span></h2><p>登録・提携順や、おすすめ順位ではありません</p></div><div id="reference-list" class="farm-grid">${eligible.length ? eligible.slice(0, visible).map(e => card(e.ref, e)).join('') : '<div class="empty-results"><h3>条件に関する公開案内が見つかりませんでした。</h3><p>キーワードや用途・品目を変えてお試しください。</p></div>'}</div>${eligible.length > visible ? `<button id="more-references" class="secondary" type="button">さらに表示（${eligible.length - visible}件）</button>` : ''}${unknown.length ? `<details class="unknown-results"><summary>用途・品目の対応が未確認の情報 <span>${unknown.length}件</span></summary><p>対応できないという意味ではありません。</p><div class="farm-grid">${unknown.map(e => card(e.ref, e)).join('')}</div></details>` : ''}${provenance}`;
        if (replaceURL) {
          const query = new URLSearchParams(); for (const [k, v] of values) if (v) query.set(k, String(v));
          history.replaceState(null, '', '/producers/' + (query.size ? '?' + query : ''));
        }
        bindCards();
        const more = document.querySelector('#more-references');
        if (more) more.onclick = () => { visible += 24; run(false, true); document.querySelector('#more-references')?.focus(); };
      };
      form.onsubmit = e => { e.preventDefault(); run(); };
      // Typing already updates the list. Replacing it when the search field blurs
      // removes the result button between pointerdown and click.
      form.onchange = event => { if (event.target !== form.elements.q) run(); };
      form.elements.q.oninput = () => run();
      document.querySelector('#reset-filters').onclick = () => { form.reset(); run(); };
      run(false);
    } else if (page === 'match') {
      main.dataset.page = 'match';
      const params = new URLSearchParams(location.search);
      if (params.get('audience')) state.request.audience = purposeName(params.get('audience'));
      if (params.get('category')) state.request.category = params.get('category');
      let step = 1;
      main.innerHTML = `<div class="wizard-shell"><a class="back-link" href="/producers/">生産者の情報から探す</a><div class="wizard-intro"><p class="eyebrow">希望を整理して、相談先を見つけよう。</p><h1>あなたの「ほしい」を<br>教えてください。</h1><p>必須なのは、用途と品目だけ。決まっていない条件は空欄で進められます。</p></div><ol class="wizard-progress" aria-label="条件入力の進み具合"><li data-step-label="1">用途・品目</li><li data-step-label="2">取引の希望</li><li data-step-label="3">候補の確認</li></ol><form id="match-form" class="wizard-form" novalidate>
      <fieldset data-step="1"><legend>何のために、何を探しますか？</legend><fieldset class="purpose-choices"><legend>利用目的 <span>必須</span></legend>${[['家庭用','home','家庭で楽しむ','旬のお取り寄せや、食べきれる量を。'],['飲食店・事業者','shop','お店・事業で使う','仕入れや継続的なお取引に。']].map(([v,i,t,d]) => `<label><input type="radio" name="audience" value="${v}" required><span>${icon(i)}<strong>${t}</strong><small>${d}</small></span></label>`).join('')}</fieldset><fieldset class="product-choices"><legend>探している農産物 <span>必須</span></legend>${categories.map(c => `<label><input type="radio" name="category" value="${c.name}" required><span>${c.name}</span></label>`).join('')}</fieldset><label class="field-label">品目・品種 <span>任意</span><input name="item" maxlength="100" placeholder="例：サラダ用の葉物、精米したお米"></label></fieldset>
      <fieldset data-step="2" hidden><legend>どんな取引を希望していますか？</legend><p class="field-help">どれも任意です。分かる範囲で入力すると、相談文にそのまま使えます。</p><div class="form-grid"><label class="field-label">希望数量<input name="quantity" maxlength="80" placeholder="例：1回に5kg、月に20袋"></label><label class="field-label">配送先の都道府県<input name="destination" maxlength="20" placeholder="例：東京都"></label><label class="field-label">納品頻度<select name="frequency"><option value="">まだ決まっていない</option><option>単発</option><option>定期</option></select></label><label class="field-label">予算／1回（税込・送料別）<input name="budget" type="number" min="1" max="100000000" step="1" placeholder="円"></label><label class="field-label">希望納品日<input name="date" type="date" min="${new Date().toLocaleDateString('sv-SE')}"></label><label class="field-label">規格・熟度・栽培方法など<input name="spec" maxlength="300" placeholder="例：加工用、規格外可、完熟"></label></div><label class="checkbox-line"><input name="smallLot" type="checkbox">少量から相談したい</label></fieldset>
      <fieldset data-step="3" hidden><legend>希望に関する案内を確認しましょう。</legend><div id="request-summary" class="request-summary"></div><div id="match-results"></div></fieldset><p id="form-error" class="form-error" role="alert"></p><div class="wizard-actions"><button type="button" id="previous-step" class="secondary" hidden>ひとつ戻る</button><button type="submit" id="next-step">取引の希望へ進む</button><a href="/compare/" id="wizard-compare" class="button" hidden>選んだ候補を比較する</a></div><p class="local-note">入力した条件はこの端末内に保存されます。生産者に送信されることはありません。</p></form></div>`;
      const form = document.querySelector('#match-form'); prefill(form, state.request);
      const showStep = n => {
        step = n;
        const currentURL = new URL(location.href);
        if (step === 1) currentURL.searchParams.delete('step'); else currentURL.searchParams.set('step', String(step));
        history.replaceState(null, '', currentURL.pathname + currentURL.search);
        form.querySelectorAll('[data-step]').forEach(el => { el.hidden = Number(el.dataset.step) !== step; });
        document.querySelectorAll('[data-step-label]').forEach(el => { if (Number(el.dataset.stepLabel) === step) el.setAttribute('aria-current', 'step'); else el.removeAttribute('aria-current'); });
        document.querySelector('#previous-step').hidden = step === 1;
        document.querySelector('#next-step').hidden = step === 3;
        document.querySelector('#next-step').textContent = step === 1 ? '取引の希望へ進む' : '相談先の情報を見る';
        document.querySelector('#wizard-compare').hidden = step !== 3;
        document.querySelector('#form-error').textContent = '';
        if (step === 3) {
          state.request = readRequest(form); persist();
          document.querySelector('#request-summary').textContent = [state.request.audience, state.request.category, state.request.item, state.request.quantity].filter(Boolean).join(' / ');
          document.querySelector('#match-results').innerHTML = resultHTML(state.request); bindCards();
        }
      };
      form.onsubmit = e => {
        e.preventDefault();
        const fields = [...form.querySelector(`[data-step="${step}"]`).querySelectorAll('input,select')];
        const invalid = fields.find(el => !el.checkValidity());
        if (invalid) { document.querySelector('#form-error').textContent = step === 1 ? '利用目的と品目を選んでください。' : '数量・予算・日付などの入力内容をご確認ください。'; invalid.focus(); return; }
        state.request = readRequest(form); persist(); showStep(Math.min(step + 1, 3));
        const heading = document.querySelector(`[data-step="${step}"] legend`); heading.tabIndex = -1; heading.focus({ preventScroll: true }); heading.scrollIntoView({ block: 'start', behavior: 'smooth' });
      };
      document.querySelector('#previous-step').onclick = () => showStep(Math.max(1, step - 1));
      form.addEventListener('change', () => { state.request = readRequest(form); persist(); });
      const requestedStep = Number(params.get('step'));
      const canResume = form.elements.audience.value && form.elements.category.value;
      showStep(canResume && [2, 3].includes(requestedStep) ? requestedStep : 1);
    } else if (page === 'compare') {
      main.dataset.page = 'compare';
      const chosen = selectedRefs();
      if (!chosen.length) emptySelection();
      else {
        const all = chosen.map(r => core.evaluate(r, state.request));
        const fieldNames = [...new Set(all.flatMap(e => e.results.map(r => r.field)))];
        main.innerHTML = `<div class="page-shell">${steps(1)}${intro('COMPARE', '気になる相談先を、<br>比べてみよう。', '公開案内と、個別に確認したいことを並べてみましょう。')}<div class="compare-controls"><a href="/producers/" class="text-button">相談先を追加する</a><a href="/match/" class="text-button">希望条件を編集する</a><span>最大3件まで比較できます</span></div><p class="table-hint" ${chosen.length === 1 ? 'hidden' : ''}>表の中を横にスクロールして比較できます。</p><div class="compare-scroll" tabindex="0" role="region" aria-label="相談先の比較表"><table class="compare-table ${chosen.length === 1 ? 'single-candidate' : ''}" style="min-width:${chosen.length === 1 ? 0 : 150 + chosen.length * 250}px"><thead><tr><th scope="col">確認すること</th>${chosen.map(r => `<th scope="col">${mini(r)}<span class="compare-region">${esc(r.region)}</span><h2>${esc(r.name)}</h2><button class="remove-candidate text-button" data-remove-ref="${r.id}">比較から外す</button></th>`).join('')}</tr></thead><tbody><tr><th scope="row">公開されている案内</th>${chosen.map(r => `<td><ul>${criteria(r).map(t => `<li>${esc(t)}</li>`).join('')}</ul></td>`).join('')}</tr>${fieldNames.map(field => `<tr><th scope="row">${esc(core.fields[field])}</th>${all.map(e => { const value = e.results.find(r => r.field === field); return `<td><span class="evidence-status ${value?.state || 'unknown'}">${value?.state === 'published' ? icon('check') + '公開案内あり' : value?.state === 'no' ? '公表条件と不一致' : '要確認'}</span><p>${esc(field === 'availability' ? '在庫・受注可否は未確認' : state.request[field] ? '希望：' + (field === 'smallLot' ? '少量から相談したい' : state.request[field]) : value?.note || '個別条件は相談時に確認してください。')}</p></td>`; }).join('')}</tr>`).join('')}<tr><th scope="row">出典・確認日</th>${chosen.map(r => `<td><button class="text-button" data-detail="${r.id}">根拠を詳しく見る</button><small>${esc(r.checked)} 確認</small></td>`).join('')}</tr></tbody></table></div>${provenance}<div class="compare-next"><div><h2>相談先が決まったら、希望を伝えよう。</h2><p>入力した条件から、公式窓口で使える相談文を準備します。</p></div><a class="button" href="/inquiry/">相談文をつくる</a></div></div>`;
        main.querySelectorAll('[data-remove-ref]').forEach(button => { button.onclick = () => { state.selected = state.selected.filter(id => id !== button.dataset.removeRef); persist(); location.reload(); }; });
        bindCards();
      }
    } else if (page === 'inquiry') {
      main.dataset.page = 'inquiry';
      const chosen = selectedRefs();
      if (!chosen.length) emptySelection();
      else {
        main.innerHTML = `<div class="page-shell">${steps(2)}${intro('GET IN TOUCH', '伝えたい希望を、<br>ひとつに。', '相談文を用意して、選んだ生産者の公式窓口へ。')}<div class="inquiry-layout"><section class="inquiry-editor"><div class="editor-heading"><h2>相談文を用意する</h2><a class="text-button" href="/match/">条件を編集する</a></div><label for="brief">必要に応じて、文章を編集できます。</label><textarea id="brief" rows="17" maxlength="6000"></textarea><p class="field-help">氏名・住所・連絡先は移動先の公式窓口で入力してください。</p><div class="inquiry-actions"><button id="copy-brief">相談文をコピー</button><button id="download-brief" class="secondary">テキスト保存</button><button id="save-brief" class="text-button">下書きに保存</button></div><p class="inquiry-notice">この画面から生産者への送信は行いません。下書きも、この端末内だけに保存されます。</p></section><aside class="inquiry-destinations"><h2>公式窓口で相談する</h2><p>相談文をコピーしたら、各公式サイトで相談を進めてください。</p>${chosen.map(r => `<article>${mini(r)}<h3>${esc(r.name)}</h3><p>${esc(r.region)}${r.categories.length ? ` / ${r.categories.map(esc).join('・')}` : ''}</p><a class="button" href="${esc(r.url)}" target="_blank" rel="noopener noreferrer" data-inquiry="producer-official">公式窓口を開く ${icon('external')}</a><span>外部サイトに移動します</span></article>`).join('')}<a class="text-button" href="/compare/">比較に戻る</a></aside></div></div>`;
        const area = document.querySelector('#brief'); area.value = core.brief(state.request, chosen);
        document.querySelector('#copy-brief').onclick = async () => {
          try { await navigator.clipboard.writeText(area.value); toast('相談文をコピーしました。公式窓口でご利用ください。'); }
          catch { area.focus(); area.select(); toast('相談文を選択しました。端末のコピー操作でコピーしてください。'); }
        };
        document.querySelector('#download-brief').onclick = () => {
          const url = URL.createObjectURL(new Blob([area.value], { type: 'text/plain;charset=utf-8' }));
          const a = document.createElement('a'); a.href = url; a.download = '農産物の相談.txt'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
        };
        document.querySelector('#save-brief').onclick = () => {
          const text = area.value.trim();
          if (!text) { toast('相談文を入力してください。'); area.focus(); return; }
          if (!state.drafts.some(d => d.text === text)) state.drafts.unshift({ id: crypto.randomUUID(), created: new Date().toISOString(), title: [state.request.item || state.request.category, 'の取引相談'].join(''), text, selected: chosen.map(r => r.id), status: 'draft' });
          state.drafts = state.drafts.slice(0, 20);
          if (persist()) toast('この端末の下書きに保存しました。生産者には送信されていません。');
        };
      }
    } else if (page === 'requests') {
      main.dataset.page = 'requests';
      main.innerHTML = `<div class="page-shell narrow-shell">${intro('YOUR DRAFTS', '相談の下書き', 'この端末に保存した、まだ送信していない相談文です。')}<div id="drafts"></div><div class="draft-bottom"><a href="/producers/" class="button">相談先を探す</a><button id="clear-drafts" class="text-button">下書きをすべて削除</button></div></div>`;
      const render = () => {
        const list = document.querySelector('#drafts'); list.innerHTML = '';
        if (!state.drafts.length) list.innerHTML = `<div class="empty-state">${icon('saved')}<h2>相談したいことを、ここに残しておこう。</h2><p>相談文をつくって「下書きに保存」を押すと、ここから見返せます。</p><a class="text-button" href="/match/">希望条件を整理する</a></div>`;
        for (const d of state.drafts) {
          const el = document.createElement('article'); el.className = 'draft-card';
          const date = new Date(d.created); const dateText = Number.isNaN(date.getTime()) ? '' : date.toLocaleDateString('ja-JP');
          el.innerHTML = `<div class="draft-card-head"><span class="draft-status">未送信の下書き</span><time>${esc(dateText)}</time><button class="icon-button" aria-label="この下書きを削除">${icon('close')}</button></div><h2>${esc(d.title || '農産物の取引相談')}</h2><details><summary>相談文を開く</summary><pre></pre></details><button class="text-button draft-copy">相談文をコピー</button>`;
          el.querySelector('pre').textContent = d.text;
          el.querySelector('.icon-button').onclick = () => { state.drafts = state.drafts.filter(x => x.id !== d.id); if (persist()) { render(); toast('下書きを削除しました。'); } };
          el.querySelector('.draft-copy').onclick = async () => { try { await navigator.clipboard.writeText(d.text); toast('相談文をコピーしました。'); } catch { el.querySelector('details').open = true; toast('相談文を開きました。選択してコピーしてください。'); } };
          list.append(el);
        }
        document.querySelector('#clear-drafts').hidden = !state.drafts.length;
      };
      document.querySelector('#clear-drafts').onclick = () => { state.drafts = []; if (persist()) render(); };
      render();
    } else if (page === 'how-it-works') {
      main.dataset.page = page;
      main.innerHTML = `<div class="page-shell narrow-shell">${intro('HOW IT WORKS', '相談までを、わかりやすく。', '産地のつながりは、農産物の相談先を探し、希望を伝える準備をするサービスです。')}<div class="guide-articles"><article>${icon('search')}<h2>農産物や用途から探す</h2><p>家庭用のお取り寄せや事業用の仕入れなど、目的に合う公開案内を探します。まだ細かな条件が決まっていなくても大丈夫です。</p><a href="/producers/">生産者の情報から探す</a></article><article>${icon('compare')}<h2>気になる相談先を比べる</h2><p>最大3件を、同じ項目で比較できます。「公開案内があること」と「あなたの希望に対応できること」は別です。個別に確認したい条件も表示します。</p><a href="/compare/">選んだ候補を見る</a></article><article>${icon('file')}<h2>相談文を持って、公式窓口へ</h2><p>希望する品目・数量・納品条件をまとめ、コピーや保存をして各公式窓口で使えます。このサイトから自動送信はしません。</p><a href="/requests/">保存した下書きを見る</a></article></div><div class="guide-faq"><h2>ご利用の前に</h2><details><summary>掲載されている生産者と提携していますか？</summary><p>現在は公式公開情報への参照です。当サイトへの参加登録や提携、掲載許諾を確認した生産者一覧ではありません。</p></details><details><summary>条件が合えば、購入や取引は確定しますか？</summary><p>確定しません。現在の在庫・受注可否・価格・送料・納品条件などは、各公式窓口で確認し、合意のうえで取引を進めてください。</p></details><details><summary>入力した内容はどこに保存されますか？</summary><p>希望条件・比較先・相談の下書きは、お使いのブラウザー内だけに保存されます。運営者や生産者に自動送信されません。フッターから削除できます。</p></details><details><summary>サイト内で購入できますか？</summary><p>購入機能は操作サンプルとして残しています。架空の商品データであり、実注文・決済・発送は行いません。</p><a href="/products/">購入サンプルを見る</a></details></div><a class="button" href="/match/">希望条件から探してみる</a></div>`;
    } else if (page === 'for-producers') {
      main.dataset.page = page;
      main.innerHTML = `<div class="page-shell narrow-shell">${intro('FOR PRODUCERS', 'つくる人と、必要とする人の間に。', '得意な品目や取引条件を、必要としている人に伝えるために。')}<div class="producer-intro"><h2>大切なのは、取引の条件が伝わること。</h2><p>品目だけでなく、小口数量、出荷時期、規格、納品頻度、対応エリアなどを分けて確認し、買い手の希望との違いを見えるようにします。</p><h2>現在の掲載範囲</h2><p>現在は、一般に公開された公式情報の参照と相談文作成に対応しています。本人確認・掲載許諾を伴う生産者登録や、サイト内の相談受付はまだ開始していません。</p><h2>登録を始める際に確認すること</h2><ul><li>本人確認と、掲載する情報の許諾</li><li>取り扱う品目、数量、規格、出荷時期</li><li>価格・支払・配送・返品などの取引条件</li><li>相談対応と、情報更新の方法</li></ul><a class="button" href="/how-it-works/">現在のサービスを見る</a></div></div>`;
    }
    updateSelection();
    document.querySelector('#clear').onclick = () => {
      try { localStorage.removeItem(key); localStorage.removeItem('agri-demo-v1'); location.href = '/requests/'; }
      catch { toast('削除できませんでした。ブラウザーのサイトデータ設定をご確認ください。'); }
    };
    return true;
  },
};
