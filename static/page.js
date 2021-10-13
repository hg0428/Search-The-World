checker = function() {
  console.log("check");
  //defaults to large becuase of :root
  if (document.documentElement.clientWidth < 850) {
    document.documentElement.setAttribute('data-width', "small");
    console.log("Small");
  } else {
    document.documentElement.setAttribute("data-width", "large");
    console.log("Large");
  }
  if (document.documentElement.clientHeight < 500) {
    document.documentElement.setAttribute("data-height", "small");
  } else {
    document.documentElement.setAttribute("data-height", "large");
  }
};
window.onresize = checker;
const Params = new URLSearchParams(window.location.search);
var pagenum = Number(Params.get("page"));

var total = Number(document.getElementById("total").innerText);

if (pagenum + 2 > total) {
  pup = document.getElementById("pageup");
  pup.classList.add('unavailable');
  pup.setAttribute("onclick", "");
}
if (pagenum - 1 < 0) {
  pdown = document.getElementById("pagedown");
  pdown.classList.add('unavailable');
  pdown.setAttribute("onclick", "");
}



function gotopage() {
  var pnum = document.getElementById("page").value;
  var q = document.getElementById("search").value;
  window.location.href = "https://search-the-world.hg0428.repl.co/?q=" + String(q) + "&page=" + String(pnum - 1);
}
//location.reload(true)
function changep(amount) {
  window.location.href = "https://search-the-world.hg0428.repl.co/?q=" + Params.get("q") + "&page=" + String(pagenum + amount);
}
document.onload = function() {
  console.log("load");
  checker();
};
