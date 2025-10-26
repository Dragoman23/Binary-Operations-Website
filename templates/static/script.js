document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("startBtn");
  if (startBtn) {
    startBtn.addEventListener("click", startQuiz);
  } else {
    loadQuestion();
  }
});

async function startQuiz() {
  const ops = Array.from(document.querySelectorAll("input[type=checkbox]:checked"))
    .map(cb => cb.value);

  const total = document.getElementById("total").value;

  const res = await fetch("/start_quiz", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      operations: ops,
      ranges: [[0,100],[0,100]], // default
      total: parseInt(total)
    })
  });

  window.location.href = "/quiz.html";
}

async function loadQuestion() {
  const q = await fetch("/next_question").then(r => r.json());

  if (q.done) {
    document.body.innerHTML = `<h2>Quiz Complete!</h2>`;
    return;
  }

  document.getElementById("question").textContent = `Q${q.qnum}: ${q.question}`;
  document.getElementById("submitBtn").onclick = async () => {
    const ans = document.getElementById("answer").value;
    const res = await fetch("/submit_answer", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({answer: ans})
    }).then(r => r.json());

    const feedback = document.getElementById("feedback");
    if (res.done) {
      feedback.textContent = `Quiz complete! You got ${res.wrong} wrong. Avg time: ${res.avg_time}s.`;
    } else if (res.correct) {
      feedback.textContent = "✅ Correct!";
      setTimeout(loadQuestion, 1000);
    } else {
      feedback.textContent = "❌ Incorrect!";
      setTimeout(loadQuestion, 1000);
    }
  };
}

