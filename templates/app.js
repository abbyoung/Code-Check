var h = document.documentElement.outerHTML;
var x = new XMLHttpRequest();
x.open('POST', '{{host_url}}api', true);
x.addEventListener('load', function (e) {
    window.location = '{{host_url}}report/'+ x.responseText;
}, false);
var d = new FormData();
d.append("html", h);
d.append("url", window.location.href);
x.send(d);
