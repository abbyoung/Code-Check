var h = document.documentElement.outerHTML;
var x = new XMLHttpRequest();
x.open('POST', 'http://sherry.local:5000/api', true);
x.addEventListener('load', function (e) {
    window.location = 'http://sherry.local:5000/report/'+ x.responseText;
}, false);
var d = new FormData();
d.append("html", h);
d.append("url", window.location.href);
x.send(d);
