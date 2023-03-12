// review.js

// Redirect user to review form with product they are reviewing 
// when they click "write a review" button
const make_review_button = document.getElementById('writeReviewBtn');
make_review_button.addEventListener('click', show_review_form);

const add_form_container = document.getElementById('add-review-form-container');
function show_review_form() {
  // If hidden, show add form
  if (add_form_container.style.display == 'none' || add_form_container.style.display == '') {
    add_form_container.style.display = 'block';
  }
  // If add form is shown, hide instead
  else {
    add_form_container.style.display = 'none';
  }
}