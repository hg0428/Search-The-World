
var sheets=["home","darkmode"];
var allsheets=[];
for (i=0;i<sheets.length;i++) {
  allsheets.push(document.getElementById(sheets[i]));
}
var current = localStorage.getItem('theme');
if(current){
  document.documentElement.setAttribute('data-theme', current);
}
document.addEventListener('DOMContentLoaded', () => {
    var checkbox = document.querySelector('input[type="checkbox"]');
    checkbox.addEventListener('change', function () {
      if (checkbox.checked) {
        current='dark'
      } else {
        current="light"
      }
      document.documentElement.setAttribute('data-theme', current);
      localStorage.setItem('theme',current)  
    });
    if (current==="dark") {
      checkbox.checked=true
    }
})