// アクセス解析（GA4）。ID が空のときと、本番の agri.shiokonbu.com 以外では何もしない。
// 入力内容などの個人情報は送らない。電話・LINE・問い合わせのリンクが押された数だけを数える（KPI：docs/strategy.md）。
(function(){
  var ID = "G-QXP10ZVT9S"; // GA4 プロパティ agri.shiokonbu.com（ストリーム agri、2026-11-03）
  if (!ID || location.hostname !== "agri.shiokonbu.com") return;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function(){ dataLayer.push(arguments); };
  gtag("js", new Date());
  gtag("config", ID);
  var s = document.createElement("script"); s.async = true;
  s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(s);
  document.addEventListener("click", function(e){
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var h = a.getAttribute("href"), ev = null;
    if (/^tel:/.test(h)) ev = "tel_click";
    else if (/line\.me|lin\.ee/.test(h)) ev = "line_click";
    else if (a.hasAttribute("data-inquiry")) ev = "inquiry_click";
    if (ev) gtag("event", ev, { provider_id: a.getAttribute("data-provider") || "", page: location.pathname });
  });
})();
