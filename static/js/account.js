// account.js

// Reference to import JS functions from another JS file: https://stackoverflow.com/questions/51763894/call-javascript-function-from-another-javascript-file
import { searchSiblingNodes } from './products.js';

function show_skin_type_form() {
  document.getElementById('skin_type_form').style.display = 'block';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
  document.getElementById('edit_target_btn').style.display = 'none';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
}

function show_skin_target_form() {
  document.getElementById('target_form').style.display = 'block';
  document.getElementById('edit_target_btn').style.display = 'none';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
}


function show_num_of_steps_form() {
  document.getElementById('num_of_steps_form').style.display = 'block';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
  document.getElementById('edit_target_btn').style.display = 'none';
}


// *********************************************************
// Add on click functionality to edit/review review buttons
// Reference: https://stackoverflow.com/questions/19655189/javascript-click-event-listener-on-class
// *********************************************************
// Remove buttons
let remove_buttons_list = document.getElementsByClassName("remove-review-btn");
for (var i = 0; i < remove_buttons_list.length; i++) {
  remove_buttons_list[i].addEventListener('click', remove_review, false);
}
// Remove a review
export function remove_review(e) {
  console.log('remove-btn clicked.')
  e = e || window.event;
  let areaClicked = e.target || e.srcElement;
  console.log(areaClicked);
  // console.log(searchSiblingNodes(areaClicked.parentElement, 'review-content'))

}

// Edit buttons
let edit_buttons_list = document.getElementsByClassName("edit-review-btn");
for (var i = 0; i < edit_buttons_list.length; i++) {
  edit_buttons_list[i].addEventListener('click', edit_review, false);
}
// Edit a review
function edit_review() {
  console.log('edit-btn clicked.')
}
