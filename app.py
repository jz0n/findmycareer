from flask import Flask, render_template, request, jsonify
from careers import careers
import random

app = Flask(__name__)

# 🎯 RIASEC Questions
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


# 🧠 Game State
def new_game():
    return {
        "scores": {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0},
        "asked": [],
        "current": None,
        "finished": False
    }


state = new_game()


# 🏠 Home route
@app.route("/")
def home():
    global state
    state = new_game()

    first = random.choice(questions)
    state["current"] = first

    return render_template("index.html", careers=careers, question=first["text"])


# 🎮 Answer route
@app.route("/answer", methods=["POST"])
def answer():
    global state

    # 🛑 Stop if already finished
    if state.get("finished"):
        return jsonify({"done": True})

    data = request.json
    choice = data.get("answer")

    current = state["current"]

    # 🎯 Update RIASEC scores
    if choice == "yes":
        state["scores"][current["type"]] += 2
    else:
        state["scores"][current["type"]] -= 1

    state["asked"].append(current)

    # 🎯 Calculate career scores
    scored = []
    for c in careers:
        score = 0
        for t, v in c["riasec"].items():
            score += state["scores"][t] * v
        scored.append((c["name"], score))

    # Sort careers
    scored.sort(key=lambda x: x[1], reverse=True)

    # 🎮 Show top 6 careers only
    top_names = [c[0] for c in scored[:6]]
    visible = [c for c in careers if c["name"] in top_names]

    # 🏁 Stop condition (after enough questions)
    if len(state["asked"]) >= 8:
        return finish()

    # 🎯 Remaining questions
    remaining = [q for q in questions if q not in state["asked"]]

    if not remaining:
        return finish()

    # 🧠 Adaptive: focus on weakest trait
    weakest = min(state["scores"], key=state["scores"].get)
    options = [q for q in remaining if q["type"] == weakest]

    next_q = random.choice(options if options else remaining)
    state["current"] = next_q

    return jsonify({
        "done": False,
        "question": next_q["text"],
        "careers": visible
    })


# 🏆 Finish game
def finish():
    global state

    scored = []

    for c in careers:
        score = 0
        for t, v in c["riasec"].items():
            score += state["scores"][t] * v
        scored.append((c, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    best = scored[0][0]
    others = [c[0] for c in scored[1:4]]  # 👈 top 3 alternatives

    state["finished"] = True

    return jsonify({
        "done": True,
        "career": best,
        "others": others
    })


# 🔁 Reset
@app.route("/reset")
def reset():
    global state
    state = new_game()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)