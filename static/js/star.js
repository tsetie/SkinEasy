// --- star buttons ---
  
// Add click event listeners to all edit buttons
document.addEventListener('DOMContentLoaded', function() {
  let stars = document.getElementsByClassName("star");
  for (var i = 0; i < stars.length; i++) {
    stars[i].addEventListener('onmouseover', star_click, false);
    stars[i].addEventListener('click', star_click, false);
  };
});


// *******************************************
// Function to handle dynamic star stylization
// *******************************************
function star_click(e) {
  // Get HTML element that was clicked
  e = e || window.event;
  console.log(e)
  let dom_clicked = e.target || e.srcElement;
  let star = dom_clicked;

  let label = dom_clicked.parentElement;
  let rating_container = label.parentElement;
  console.log(rating_container)
  let kids = rating_container.children;
  console.log(kids)

  let rating_input = label.querySelector("input[name=rating]:checked");
  let rating_value = rating_input.value;

  console.log(label.querySelector("input[name=rating]:checked").value)
  
  for (var i = 0; i < rating_value; i++) {
    console.log('yellow star');
    kids[kids.length-1-i].style.color = "#ffe137";
    kids[kids.length-1-i].style.opacity = 1;
  }

  for (var i = rating_value; i < 5; i++) {
    console.log('no star');
    kids[kids.length-1-i].style.color = "#949494";
    kids[kids.length-1-i].style.opacity = 0.5;
  }

  label.querySelector
}

