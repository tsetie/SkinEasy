// quiz.js

// --- Functions to toggle showing quiz form ---
// 1) Opening the quiz form
const take_quiz_btn = document.getElementById("take-quiz-btn");
take_quiz_btn.addEventListener("click", showQuiz);
function showQuiz() {
  document.getElementById("myForm").style.display = "block";
}
// 2) Closing the quiz form
const close_quiz_btn = document.getElementById("close-quiz-btn");
close_quiz_btn.addEventListener("click", closeQuiz);
function closeQuiz() {
  document.getElementById("myForm").style.display = "none";
}