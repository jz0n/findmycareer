from flask import Flask, render_template, request, jsonify
from careers import careers
import random

app = Flask(__name__)

# RIASEC Questions
questions = [
    {"text": "Do you enjoy building or fixing things?", "type": "R"},
    {"text": "Do you like working outdoors?", "type": "R"},

    {"text": "Do you enjoy solving problems or puzzles?", "type": "I"},
    {"text": "Do you like science or research?", "type": "I"},

    {"text": "Are you creative or artistic?", "type": "A"},
    {"text": "Do you enjoy music or design?", "type": "A"},

    {"text": "Do you enjoy helping people?", "type": "S"},
    {"text": "Do you like teaching or guiding others?", "type": "S"},

    {"text": "Do you enjoy leading or persuading?", "type": "E"},
    {"text": "Do you like business or sales?", "type": "E"},

    {"text": "Do you enjoy organizing or working with data?", "type": "C"},
    {"text": "Do you like structured tasks?", "type": "C"},
]


def new_game():
    return {
        "scores": {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0},
        "asked": [],
        "current": None
    }

state = new_game()


@app.route("/")
def home():
    global state
    state = new_game()

    first = random.choice(questions)
    state["current"] = first

    return render_template("index.html", careers=careers, question=first["text"])


@app.route("/answer", methods=["POST"])
def answer():
    global state

    data = request.json
    choice = data.get("answer")

    current = state["current"]

    # Update scores
    if choice == "yes":
        state["scores"][current["type"]] += 2
    else:
        state["scores"][current["type"]] -= 1

    state["asked"].append(current)

    # Stop after 8 questions
    if len(state["asked"]) >= 8:
        return finish()

    # Remaining questions
    remaining = [q for q in questions if q not in state["asked"]]

    if not remaining:
        return finish()

    # Adaptive: focus on weakest trait
    weakest = min(state["scores"], key=state["scores"].get)

    options = [q for q in remaining if q["type"] == weakest]

    next_q = random.choice(options if options else remaining)
    state["current"] = next_q

    return jsonify({
        "done": False,
        "question": next_q["text"]
    })


def finish():
    global state

    best = None
    best_score = -999

    for c in careers:
        score = 0
        for t, v in c["riasec"].items():
            score += state["scores"][t] * v

        if score > best_score:
            best_score = score
            best = c

    return jsonify({
        "done": True,
        "career": best
    })


@app.route("/reset")
def reset():
    global state
    state = new_game()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)