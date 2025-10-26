from flask import Flask, render_template, request, jsonify, session
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Helper Functions ---
def generate_question(operation, ranges):
    """Return a new math question and its answer."""
    r = ranges[operation]
    if operation == "a":
        n1 = random.randint(*r[0])
        n2 = random.randint(*r[1])
        return {"question": f"{n1} + {n2}", "answer": n1 + n2}
    elif operation == "s":
        n1 = random.randint(*r[0])
        n2 = random.randint(0, n1)
        return {"question": f"{n1} - {n2}", "answer": n1 - n2}
    elif operation == "m":
        n1 = random.randint(*r[0])
        n2 = random.randint(*r[1])
        return {"question": f"{n1} × {n2}", "answer": n1 * n2}
    elif operation == "d":
        n1 = random.randint(*r[0])
        n2 = random.randint(max(1, r[1][0]), r[1][1])  # avoid zero
        n1 -= n1 % n2  # make divisible
        return {"question": f"{n1} ÷ {n2}", "answer": n1 // n2}
    else:
        raise ValueError("Unsupported operation")

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    data = request.json
    operations = data["operations"]  # ["a","s"]
    ranges = data["ranges"]          # {"a":[[0,10],[0,10]], "s":[[0,20],[0,20]]}
    total = int(data["total"])

    session["operations"] = operations
    session["ranges"] = ranges
    session["total"] = total
    session["wrong"] = 0
    session["count"] = 0
    session["start_time"] = datetime.now().timestamp()

    return jsonify({"status": "started"})

@app.route("/next_question")
def next_question():
    if session["count"] >= session["total"]:
        return jsonify({"done": True})

    operation = random.choice(session["operations"])
    question_data = generate_question(operation, session["ranges"])
    session["current_answer"] = question_data["answer"]
    session["current_operation"] = operation
    session["count"] += 1

    return jsonify({
        "done": False,
        "question": question_data["question"],
        "qnum": session["count"]
    })

@app.route("/submit_answer", methods=["POST"])
def submit_answer():
    data = request.json
    player_answer = data["answer"]
    correct_answer = session["current_answer"]

    # Handle mistakes count
    if "mistakes" not in session:
        session["mistakes"] = 0

    if str(player_answer).strip() == str(correct_answer):
        correct = True
        session["mistakes"] = 0
    else:
        correct = False
        session["wrong"] += 1
        session["mistakes"] += 1

    # If wrong twice, generate a new question but keep question number
    if session["mistakes"] >= 2:
        operation = session["current_operation"]
        question_data = generate_question(operation, session["ranges"])
        session["current_answer"] = question_data["answer"]
        session["mistakes"] = 0
        return jsonify({"done": False, "correct": False, "new_question": question_data["question"]})

    if session["count"] >= session["total"]:
        end_time = datetime.now().timestamp()
        duration = end_time - session["start_time"]
        avg_time = round(duration / session["total"], 2)

        return jsonify({
            "done": True,
            "wrong": session["wrong"],
            "total": session["total"],
            "avg_time": avg_time
        })

    return jsonify({"done": False, "correct": correct})

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port])

