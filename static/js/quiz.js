
const show_quiz_btn = document.getElementById("take-quiz-btn");
show_quiz_btn.addEventListener("click", showQuiz);
function showQuiz() {
  document.getElementById("myForm").style.display = "block";
}



// Functionality to add popup form when clicked
function openForm() {
    document.getElementById("myForm").style.display = "block";
  }
  
  function closeForm() {
    document.getElementById("myForm").style.display = "none";
  }