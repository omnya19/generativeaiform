function addQuestion() {
  const numQuestionsInput = document.getElementById("num_questions");
  const questionsContainer = document.getElementById("questionsContainer");
  const numQuestions = parseInt(numQuestionsInput.value);

  if (!isNaN(numQuestions) && numQuestions > 0) {
    questionsContainer.innerHTML = "";

    for (let i = 1; i <= numQuestions; i++) {
      const questionDiv = document.createElement("div");
      questionDiv.classList.add("question-container"); // Add the question-container class

      const questionLabel = document.createElement("label");
      questionLabel.setAttribute("for", `question_${i}`);

      questionLabel.textContent = `Enter Question${i}: `;

      const questionInput = document.createElement("input");
      questionInput.setAttribute("type", "text");
      questionInput.setAttribute("id", `question_${i}`);
      questionInput.setAttribute("name", `question_${i}`);
      questionInput.setAttribute("required", true);

      const answerLabel = document.createElement("label");
      answerLabel.setAttribute("for", `answer_${i}`);
      answerLabel.textContent = `Enter Answer ${i}: `;

      const answerInput = document.createElement("input");
      answerInput.setAttribute("type", "text");
      answerInput.setAttribute("id", `answer_${i}`);
      answerInput.setAttribute("name", `answer_${i}`);
      answerInput.setAttribute("required", true);

      questionDiv.appendChild(questionLabel);
      questionDiv.appendChild(questionInput);
      questionDiv.appendChild(answerLabel);
      questionDiv.appendChild(answerInput);
      questionsContainer.appendChild(questionDiv);
    }
  }
}
