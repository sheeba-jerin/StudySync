from flask import Flask, render_template, request, redirect, url_for, flash
import os, json, random
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import send_from_directory

# AI Predictor
from ai.predictor import predict_exam_performance

app = Flask(__name__)
app.secret_key = "studysync_secret"

UPLOAD_FOLDER = "uploads"
TASK_FILE = "planner_tasks.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- UTILITIES ----------------
def load_tasks():
    if not os.path.exists(TASK_FILE):
        with open(TASK_FILE, "w") as f:
            json.dump([], f)

    with open(TASK_FILE, "r") as f:
        tasks = json.load(f)

    now = datetime.now()
    updated = False

    for t in tasks:
        task_time = datetime.strptime(t["datetime"], "%Y-%m-%d %H:%M")

        t.setdefault("done", False)
        t.setdefault("locked", False)
        t.setdefault("overdue", False)

        if not t["done"] and task_time < now:
            t["overdue"] = True
            t["locked"] = True
            updated = True

        if t["done"]:
            t["locked"] = True

    if updated:
        save_tasks(tasks)

    return tasks


def save_tasks(tasks):
    with open(TASK_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


# ---------------- PLANNER ----------------
@app.route("/planner", methods=["GET", "POST"])
def planner():
    tasks = load_tasks()

    if request.method == "POST":
        tasks.append({
            "subject": request.form["subject"],
            "datetime": f"{request.form['date']} {request.form['time']}",
            "done": False,
            "locked": False,
            "overdue": False
        })
        save_tasks(tasks)
        return redirect(url_for("planner"))

    return render_template("planner.html", tasks=tasks)


@app.route("/delete_task/<int:index>")
def delete_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks) and not tasks[index]["locked"]:
        tasks.pop(index)
        save_tasks(tasks)
    return redirect(url_for("planner"))


@app.route("/toggle_task/<int:index>")
def toggle_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks) and not tasks[index]["locked"]:
        tasks[index]["done"] = True
        tasks[index]["locked"] = True
        save_tasks(tasks)
    return redirect(url_for("progress"))


# ---------------- NOTES ----------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/notes", methods=["GET", "POST"])
def notes():
    metadata_file = os.path.join(app.config["UPLOAD_FOLDER"], "notes_metadata.json")

    notes_metadata = []
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            notes_metadata = json.load(f)

    if request.method == "POST":
        file = request.files["file"]
        title = request.form.get("title") or file.filename
        filename = secure_filename(file.filename)

        if any(n["filename"] == filename for n in notes_metadata):
            flash("File already exists!", "error")
        else:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            notes_metadata.append({"title": title, "filename": filename})
            with open(metadata_file, "w") as f:
                json.dump(notes_metadata, f)
            flash("File uploaded successfully!", "success")

        return redirect(url_for("notes"))

    return render_template("notes.html", notes=notes_metadata)


@app.route("/delete_note/<filename>")
def delete_note(filename):
    metadata_file = os.path.join(app.config["UPLOAD_FOLDER"], "notes_metadata.json")

    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            notes_metadata = json.load(f)
    else:
        notes_metadata = []

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        notes_metadata = [n for n in notes_metadata if n["filename"] != filename]
        with open(metadata_file, "w") as f:
            json.dump(notes_metadata, f)

    return redirect(url_for("notes"))


# ---------------- PROGRESS ----------------
@app.route("/progress")
def progress():
    tasks = load_tasks()
    total = len(tasks)
    completed = sum(1 for t in tasks if t["done"])

    return render_template(
        "progress.html",
        tasks=tasks,
        total=total,
        completed=completed
    )


# ---------------- AI EXAM PREDICTOR ----------------
@app.route("/ai-predict", methods=["GET", "POST"])
def ai_predict():
    result = None

    if request.method == "POST":
        predicted_score, level, suggestions = predict_exam_performance(
            float(request.form["study_hours"]),
            float(request.form["attendance"]),
            float(request.form["assignments"]),
            float(request.form["previous_score"])
        )

        result = {
            "score": predicted_score,
            "level": level,
            "suggestions": suggestions
        }

    return render_template("ai_predict.html", result=result)


# ---------------- AI STUDY PLAN ----------------
@app.route("/ai-study-plan")
def ai_study_plan():
    tasks = load_tasks()
    now = datetime.now()
    plan = []

    insight_pool = {
        "high": [
            "🔥 Cognitive overload detected. Prioritize deep focus sessions.",
            "⚠️ Risk of last-minute stress. Split work into micro-tasks.",
            "🚀 Peak performance window needed. Avoid multitasking."
        ],
        "medium": [
            "📘 Balanced workload. Reinforce understanding with active recall.",
            "🧠 Stable progress expected. Maintain consistency.",
            "⏳ Moderate urgency. Short daily revisions recommended."
        ],
        "low": [
            "🗓️ Low cognitive pressure. Passive review is enough.",
            "📖 Long-term retention phase. Space repetition weekly.",
            "🌱 Concept incubation stage. No rush required."
        ]
    }

    for t in tasks:
        if t["done"] or t["locked"]:
            continue

        deadline = datetime.strptime(t["datetime"], "%Y-%m-%d %H:%M")
        hours_left = max((deadline - now).total_seconds() / 3600, 1)

        workload_density = len(tasks)
        priority_score = round((1 / hours_left) * (workload_density / 5), 3)
        suggested_hours = round(min(3.0, max(0.5, priority_score * 4)), 1)

        if priority_score > 0.8:
            insight = random.choice(insight_pool["high"])
        elif priority_score > 0.3:
            insight = random.choice(insight_pool["medium"])
        else:
            insight = random.choice(insight_pool["low"])

        plan.append({
            "subject": t["subject"],
            "deadline": t["datetime"],
            "priority": priority_score,
            "suggested_hours": suggested_hours,
            "insight": insight
        })

    plan.sort(key=lambda x: x["priority"], reverse=True)
    return render_template("ai_study_plan.html", plan=plan)


# ---------------- AI FAILURE RISK MONITOR (REAL AI) ----------------
@app.route("/ai-risk")
def ai_risk():
    tasks = load_tasks()

    total_tasks = len(tasks)
    overdue = sum(1 for t in tasks if t["overdue"])
    incomplete = sum(1 for t in tasks if not t["done"])
    workload_pressure = min((incomplete / max(total_tasks, 1)) * 100, 100)

    # Risk calculation (multi-factor)
    risk = round(
        (overdue * 15) +
        (workload_pressure * 0.5),
        2
    )

    risk = min(risk, 100)

    if risk >= 70:
        level = "High Risk"
        insight = "🚨 Severe academic risk detected. Immediate intervention required."
    elif risk >= 40:
        level = "Moderate Risk"
        insight = "⚠️ Performance instability observed. Improve consistency."
    else:
        level = "Low Risk"
        insight = "✅ Healthy academic state. Maintain current habits."

    graph = [
        100 - workload_pressure,
        70 if overdue else 30,
        60,
        workload_pressure
    ]

    result = {
        "risk": risk,
        "level": level,
        "tasks": total_tasks,
        "insight": insight,
        "graph": graph
    }

    return render_template("ai_risk.html", result=result)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
