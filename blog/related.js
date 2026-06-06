(function () {
  var path = window.location.pathname;
  var slug = path.replace(/^\/blog\//, '').replace(/\/+$/, '').replace(/\/index\.html$/, '');
  var catEl = document.querySelector('.post-category');
  var currentCat = catEl ? catEl.textContent.trim() : '';

  var css = [
    '.yml-section{margin:56px 0 0;padding-top:40px;border-top:1px solid rgba(27,0,9,.08)}',
    '.yml-label{display:block;font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#6b5a4e;margin-bottom:20px}',
    '.yml-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}',
    '.yml-card{background:#FEFCF8;border:1.5px solid rgba(27,0,9,.1);padding:22px;text-decoration:none;display:flex;flex-direction:column;gap:8px;transition:border-color .15s,transform .15s}',
    '.yml-card:hover{border-color:#C5442C;transform:translateY(-2px)}',
    '.yml-card-cat{font-size:10px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#C5442C}',
    '.yml-card-title{font-family:"DM Serif Display",serif;font-size:17px;line-height:1.25;color:#1B0009}',
    '.yml-card-meta{font-size:11px;color:#6b5a4e}',
    '.yml-card-arrow{font-size:13px;font-weight:700;color:#C5442C;margin-top:4px}'
  ].join('');

  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  fetch('/blog/posts.json')
    .then(function (r) { return r.json(); })
    .then(function (posts) {
      var others = posts.filter(function (p) { return p.slug !== slug; });
      if (!others.length) return;

      others.sort(function (a, b) {
        var aS = a.category === currentCat ? 0 : 1;
        var bS = b.category === currentCat ? 0 : 1;
        if (aS !== bS) return aS - bS;
        return b.date.localeCompare(a.date);
      });

      var picks = others.slice(0, 3);

      var cards = picks.map(function (p) {
        var d = new Date(p.date);
        var dateStr = months[d.getUTCMonth()] + ' ' + d.getUTCDate() + ', ' + d.getUTCFullYear();
        return '<a href="/blog/' + p.slug + '/" class="yml-card">' +
          '<span class="yml-card-cat">' + p.category + '</span>' +
          '<span class="yml-card-title">' + p.title + '</span>' +
          '<span class="yml-card-meta">' + dateStr + ' &nbsp;&middot;&nbsp; ' + p.reading_time + ' min read</span>' +
          '<span class="yml-card-arrow">Read &rarr;</span>' +
          '</a>';
      }).join('');

      var section = document.createElement('div');
      section.className = 'yml-section';
      section.innerHTML = '<span class="yml-label">You might also like</span><div class="yml-grid">' + cards + '</div>';

      var body = document.querySelector('.post-body');
      if (body) body.appendChild(section);
    })
    .catch(function () {});
})();
