function gotopage() {
  var pnum = document.getElementById("page").value;
  var q = document.getElementById("search").value;
  window.location.href = "https://search-the-world.projxon.repl.co/?q="+String(q)+"&page="+String(pnum-1);
}