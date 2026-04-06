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

    # Safety check
    if state["index"] >= len(questions):
        return jsonify({"done": True})

    tag = questions[state["index"]]["tag"]

    # Score careers
    for c in careers:
        if tag in c["tags"]:
            if choice == "yes":
                state["scores"][c["name"]] += 1
            else:
                state["scores"][c["name"]] -= 0.5

    state["index"] += 1

    # Sort careers
    sorted_list = sorted(state["scores"].items(), key=lambda x: x[1], reverse=True)
    top_names = [c[0] for c in sorted_list[:10]]
    filtered = [c for c in careers if c["name"] in top_names]

    # End condition
    if state["index"] >= len(questions):
        best = [c for c in careers if c["name"] in [x[0] for x in sorted_list[:3]]]

        return jsonify({
            "done": True,
            "careers": best
        })

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