from flask import Flask, render_template, request, jsonify
from careers import careers, questions

app = Flask(__name__)

def new_game():
    return {
        "scores": {c["name"]: 0 for c in careers},
        "index": 0
    }

state = new_game()


@app.route("/")
def home():
    return render_template("index.html", careers=careers, question=questions[0])


@app.route("/answer", methods=["POST"])
def answer():
    global state

    data = request.json
    choice = data["answer"]

    if state["index"] >= len(questions):
        return jsonify({"done": True})

    q = questions[state["index"]]
    tag = q["tag"]
    weight = q["weight"]

    for c in careers:
        tags = c["tags"]

        if tag in tags:
            if choice == "yes":
                state["scores"][c["name"]] += weight * 3
            else:
                state["scores"][c["name"]] -= weight * 2
        else:
            if choice == "yes":
                state["scores"][c["name"]] -= 1

    state["index"] += 1

    sorted_list = sorted(state["scores"].items(), key=lambda x: x[1], reverse=True)

    best_name, best_score = sorted_list[0]

    total_possible = sum(q["weight"] * 3 for q in questions)
    confidence = int((best_score / total_possible) * 100)

    best_career = next(c for c in careers if c["name"] == best_name)
    best_career["match"] = max(0, confidence)

    if state["index"] >= len(questions):
        return jsonify({
            "done": True,
            "career": best_career
        })

    top_names = [c[0] for c in sorted_list[:10]]
    filtered = [c for c in careers if c["name"] in top_names]

    return jsonify({
        "done": False,
        "careers": filtered,
        "question": questions[state["index"]]["question"]
    })

@app.route("/reset")
def reset():
    global state
    state = new_game()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)