function show_skin_type_form(){
  document.getElementById('skin_type_form').style.display = 'block';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
  document.getElementById('edit_target_btn').style.display = 'none';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
}

function show_skin_target_form(){
  document.getElementById('target_form').style.display = 'block';
  document.getElementById('edit_target_btn').style.display = 'none';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
}


function show_num_of_steps_form(){
  document.getElementById('num_of_steps_form').style.display = 'block';
  document.getElementById('edit_num_of_steps_btn').style.display = 'none';
  document.getElementById('edit_skin_type_btn').style.display = 'none';
  document.getElementById('edit_target_btn').style.display = 'none';
}