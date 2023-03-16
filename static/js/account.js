// account.js


// *****************************************************************************
// Functions to show and hide user preference forms
const edit_skin_type_btn = document.getElementById('edit_skin_type_btn');
edit_skin_type_btn.addEventListener('click',  show_skin_type_form);
function show_skin_type_form() {
  document.getElementById('skin_type_form').style.display = 'block';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
  document.getElementById('edit_target_btn').style.display = 'none';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
}

const edit_target_btn = document.getElementById('edit_target_btn');
edit_target_btn.addEventListener('click',  show_skin_target_form);
function show_skin_target_form() {
  document.getElementById('target_form').style.display = 'block';
  document.getElementById('edit_target_btn').style.display = 'none';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
}

const edit_num_of_steps_btn = document.getElementById('edit_num_of_steps_btn');
edit_num_of_steps_btn.addEventListener('click',  show_num_of_steps_form);
function show_num_of_steps_form() {
  document.getElementById('num_of_steps_form').style.display = 'block';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
  document.getElementById('edit_target_btn').style.display = 'none';
}
// *****************************************************************************


// **********************************************************************************
// Function to get three necessary components for review edit/delete
// Input(s):
//  * dom_clicked           (Node):     area on document that was clicked
//  * main_container_class  (String):   class name of main container
//  * card_class            (String):   class name of card container
//  * id_name               (String):   class name of ID div with ID value to send
// **********************************************************************************
function get_containers_and_id(dom_clicked, main_container_class, card_class, id_name) {
  // Get main container of review content
  let dom_node = dom_clicked;
  let card_container = null;
  // Look through parent elements until we find main container class
  while (!(dom_node.className.match(main_container_class))) {
    // Look for review ID container as we look for the main review container
    if ((dom_node != null) && (dom_node.className.match(card_class))) {
      card_container = dom_node;
    } 
    // Move to next node
    dom_node = dom_node.parentElement;
  }
  // Set review container in more readable variable
  let main_box = dom_node;
  // Search for specified ID
  let card_children = card_container.children;
  let id = null;
  for (var i = 0; i < card_children.length; i++) {
    // Look for id container with the passed in ID 
    if ((card_children[i] != null) && (card_children[i].className == id_name)) {
      id = card_children[i].innerText;
      break;
    }
  }
  // Return the main container, the card container, and the ID we want
  return { main_box: main_box, card: card_container, id: Number(id) };
}



// ****************************************************************************************************************************************************
// Add on click functionality to edit/review review buttons
// Reference(s): 
//  * Reference to add event listener to a class of buttons:  https://stackoverflow.com/questions/19655189/javascript-click-event-listener-on-class
//  * Reference to execfute function after page load:         https://stackoverflow.com/questions/11936816/execute-function-after-complete-page-load
// ****************************************************************************************************************************************************
document.addEventListener('DOMContentLoaded', function() {
  // --- Remove buttons ---
  // Add click event listeners to all remove buttons
  let remove_buttons_list = document.getElementsByClassName('remove-review-btn');
  for (var i = 0; i < remove_buttons_list.length; i++) {
    remove_buttons_list[i].addEventListener('click', remove_review, false);
  };
  // --- Edit buttons ---
  // Add click event listeners to all edit buttons
  let edit_buttons_list = document.getElementsByClassName("edit-review-btn");
  for (var i = 0; i < edit_buttons_list.length; i++) {
    edit_buttons_list[i].addEventListener('click', edit_review, false);
  };
  // --- star buttons ---
  // Add click event listeners to all edit buttons
  let stars = document.getElementsByClassName("star");
  for (var i = 0; i < stars.length; i++) {
    stars[i].addEventListener('onmouseover', star_click, false);
    stars[i].addEventListener('click', star_click, false);
  };
});


// ***********************************************************************************************************************************************************
// Function to remove a review
//  * Reference to remove an HTML element dynamically:        https://stackoverflow.com/questions/12287422/removing-element-dynamically
//  * Reference to convert JS string to number:               https://stackoverflow.com/questions/1133770/how-to-convert-a-string-to-an-integer-in-javascript
// ***********************************************************************************************************************************************************
function remove_review(e) {
  // Get HTML element that was clicked
  e = e || window.event;
  let dom_clicked = e.target || e.srcElement;
  
  // Get review main container, card container, and ID 
  boxes_and_id = get_containers_and_id(dom_clicked, 'review-entry-box', 'review-card', 'review-id');
  let review_entry_box  = boxes_and_id['main_box'];
  let review_id         = boxes_and_id['id'];

  // Remove review from HTML so users see changes without page reload
  let review_entry_box_parent = review_entry_box.parentElement;
  review_entry_box_parent.removeChild(review_entry_box);

  // Update review number counter in review header
  let review_count = document.getElementById('user-review-count');
  review_count.innerHTML = Number(review_count.innerText) - 1;


  // Send POST request to server w/ review ID as data so we know which review to delete
  const data = { review_id: Number(review_id) };

  // Make post request to delete selected product from user's routine table
  fetch("/delete_review", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((responseData) => {
      console.log("Success:", responseData);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}


// ***************************
// Function to edit a review
// Reference(s):
//  * https://stackoverflow.com/questions/16302045/finding-child-element-of-parent-with-javascript
//  * https://www.geeksforgeeks.org/how-to-append-html-code-to-a-div-using-javascript/
//  * https://developer.mozilla.org/en-US/docs/web/html/global_attributes/contenteditable
//  * https://stackoverflow.com/questions/27466969/how-to-add-attribute-to-html-element-using-javascript
// ***************************
function edit_review(e) {
  // Get HTML element that was clicked
  e = e || window.event;
  let dom_clicked = e.target || e.srcElement;

  // Get review main container, card container, and ID 
  boxes_and_id = get_containers_and_id(dom_clicked, 'review-entry-box', 'review-card', 'product-id');
  let review_entry_box  = boxes_and_id['main_box'];
  let review_card       = boxes_and_id['card'];
  let review_id         = boxes_and_id['id'];

  // Add product ID to form inputs
  let product_id_box  = review_entry_box.querySelector('.product-id');
  let product_id      = Number(product_id_box.innerHTML);
  let form_card       = review_card.querySelector('.empty_product_id_container');
  form_card.innerHTML = `
    <div id="product-id-container">
        <input type="text" name="product-id" value=`+product_id+`>
    </div>
  `;

  // Get edit button div
  let edit_button_txt = review_card.querySelector('.edit-txt');

  // Toggle between original review and edit form
  let old_review = review_card.querySelector('.old-review');
  let new_review = review_card.querySelector('.new-review');
  console.log("Old: " + old_review);
  console.log("New: " +  new_review);
  // Show original review
  if (old_review.style.display == 'none') {
    old_review.style.display = 'block';
    new_review.style.display = 'none';
    edit_button_txt.innerText = 'Edit';
  // Show edit form
  } else {
    old_review.style.display = 'none';
    new_review.style.display = 'block';
    edit_button_txt.innerText = 'Cancel';
  }
  

}

