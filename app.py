from flask import Flask, render_template, request, jsonify
from careers import careers

app = Flask(__name__)

# Question bank (by tag)
tag_questions = {
    "people": "Do you enjoy working with people?",
    "math": "Do you enjoy math and logical thinking?",
    "creative": "Are you creative?",
    "outdoor": "Do you like working outdoors?",
    "science": "Are you interested in science?",
    "tech": "Do you enjoy technology?"
}

# Initialize game state
def new_game():
    return {
        "scores": {c["name"]: 0 for c in careers},
        "index": 0,
        "last_tag": None,
        "asked_tags": set()
    }

state = new_game()


@app.route("/")
def home():
    first_question = "Answer a few questions to find your career!"
    return render_template("index.html", careers=careers, question=first_question)


@app.route("/answer", methods=["POST"])
def answer():
    global state

    data = request.json
    choice = data.get("answer")

    # Apply previous answer
    if state["last_tag"] is not None:
        tag = state["last_tag"]

        for c in careers:
            if tag in c["tags"]:
                if choice == "yes":
                    state["scores"][c["name"]] += 3
                else:
                    state["scores"][c["name"]] -= 2
            else:
                if choice == "yes":
                    state["scores"][c["name"]] -= 1

    # Sort careers
    sorted_list = sorted(state["scores"].items(), key=lambda x: x[1], reverse=True)

    # 🎯 STOP: clear winner
    if len(sorted_list) > 1:
        gap = sorted_list[0][1] - sorted_list[1][1]
        if gap >= 8:
            best_name = sorted_list[0][0]
            best_career = next(c for c in careers if c["name"] == best_name)

            return jsonify({
                "done": True,
                "career": best_career
            })

    # 🎯 STOP: max questions
    if state["index"] >= 10:
        best_name = sorted_list[0][0]
        best_career = next(c for c in careers if c["name"] == best_name)

        return jsonify({
            "done": True,
            "career": best_career
        })

    # 🎯 Choose best next tag (adaptive)
    tag_counts = {}

    for c in careers:
        for tag in c["tags"]:
            if tag not in state["asked_tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # If no tags left → stop
    if not tag_counts:
        best_name = sorted_list[0][0]
        best_career = next(c for c in careers if c["name"] == best_name)

        return jsonify({
            "done": True,
            "career": best_career
        })

    # Pick tag that best splits careers
    total = len(careers)
    best_tag = None
    best_diff = float("inf")

    for tag, count in tag_counts.items():
        diff = abs((total / 2) - count)
        if diff < best_diff:
            best_diff = diff
            best_tag = tag

    # Save state
    state["last_tag"] = best_tag
    state["asked_tags"].add(best_tag)
    state["index"] += 1

    # Show top careers visually
    top_names = [c[0] for c in sorted_list[:10]]
    visible = [c for c in careers if c["name"] in top_names]

    return jsonify({
        "done": False,
        "careers": visible,
        "question": tag_questions.get(best_tag, "Do you enjoy this type of work?")
    })


@app.route("/reset")
def reset():
    global state
    state = new_game()
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(debug=True)