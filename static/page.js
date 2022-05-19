checker = function() {
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
console.log("on!");
const tabs = ["all", "images"];

function TabSwitch(tab) {
  document.getElementById("tab-" + tab).classList.add("active-tab");
  for (i = 0; i < tabs.length; i++) {
    document.getElementById("tab-" + tabs[i]).classList.remove("active-tab");
  }
};
