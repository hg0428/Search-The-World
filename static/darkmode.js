
var current = localStorage.getItem('theme');
if (!current) {
  current = "light";
}
var checkbox = document.querySelector('input[type="checkbox"]');

function SetColour(current) {
  var checkbox = document.querySelector('input[type="checkbox"]');
  document.documentElement.setAttribute("theme", current);
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
}

function GetPreferredColorScheme() {
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
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    current = e.matches ? "dark" : "light";
    SetColour(current);
});
}

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