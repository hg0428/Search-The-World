/*var script = document.createElement('script'); 
script.src="//cdn.jsdelivr.net/npm/eruda"; 
document.body.appendChild(script); 
script.onload = function () { eruda.init() } 
*/


var sheets = ["home", "darkmode"];
var allsheets = [];
for (let i = 0; i < sheets.length; i++) {
  allsheets.push(document.getElementById(sheets[i]));
}
var current = localStorage.getItem('theme');
if (!current) {
  current = "light";
}
var checkbox = document.querySelector('input[type="checkbox"]');

function SetColour(current) {
  var checkbox = document.querySelector('input[type="checkbox"]');
  if (current) {
    document.documentElement.setAttribute('data-theme', current);
    if (current === "dark") {
      checkbox.checked = true;
      document.querySelector('meta[name="theme-color"]').setAttribute("content", "#191919");

    } else {
      checkbox.checked = false;
      document.querySelector('meta[name="theme-color"]').setAttribute("content", "#f5f5f5");
    }
  }
  console.log("change");
}

function GetPreferredColorScheme() {
  console.log("seeking");
  if (window.matchMedia) {
    // Check if the dark-mode Media-Query matches
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      current = "dark";
    } else {
      current = "light";
    }
  }
  SetColour(current);
}


if (window.matchMedia) {
  console.log(true);
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    current = e.matches ? "dark" : "light";
    SetColour(current);
});
}


console.log("loaded!");
checkbox.addEventListener('change', function() {
  if (checkbox.checked) {
    current = 'dark';
  } else {
    current = 'light';
  }
  localStorage.setItem('theme', current);
  SetColour(current);
});
GetPreferredColorScheme();
