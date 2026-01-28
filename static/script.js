document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("plannerForm");
    const taskList = document.getElementById("taskList");

    if (!form) return; // safety check

    let tasks = JSON.parse(localStorage.getItem("studyTasks")) || [];

    function renderTasks() {
        taskList.innerHTML = "";
        tasks.forEach((task, index) => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";

            li.innerHTML = `
                <div>
                    <strong>${task.subject}</strong><br>
                    <small>${task.date} at ${task.time}</small>
                </div>
                <button class="btn btn-sm btn-danger">❌</button>
            `;

            li.querySelector("button").onclick = () => {
                tasks.splice(index, 1);
                saveTasks();
            };

            taskList.appendChild(li);
        });
    }

    function saveTasks() {
        localStorage.setItem("studyTasks", JSON.stringify(tasks));
        renderTasks();
    }

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const date = document.getElementById("date").value;
        const subject = document.getElementById("subject").value;
        const time = document.getElementById("time").value;

        tasks.push({ date, subject, time });
        saveTasks();
        form.reset();
    });

    renderTasks();
});
// ===== NOTES FEATURE =====
const notesForm = document.getElementById("notesForm");
const notesList = document.getElementById("notesList");
const warningText = document.getElementById("warningText");

if (notesForm) {
    let notes = JSON.parse(localStorage.getItem("uploadedNotes")) || [];

    function renderNotes() {
        notesList.innerHTML = "";
        notes.forEach((note, index) => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";

            li.innerHTML = `
                <div>
                    <strong>${note.name}</strong><br>
                    <small>${note.type}</small>
                </div>
                <button class="btn btn-sm btn-danger">❌</button>
            `;

            li.querySelector("button").onclick = () => {
                notes.splice(index, 1);
                saveNotes();
            };

            notesList.appendChild(li);
        });
    }

    function saveNotes() {
        localStorage.setItem("uploadedNotes", JSON.stringify(notes));
        renderNotes();
    }

    notesForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const fileInput = document.getElementById("noteFile");
        const file = fileInput.files[0];

        if (!file) return;

        // File size warning (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            warningText.textContent = "⚠ File too large! Maximum 5MB allowed.";
            return;
        } else {
            warningText.textContent = "";
        }

        notes.push({ name: file.name, type: file.type });
        saveNotes();
        fileInput.value = "";
    });

    renderNotes();
}
// ===== NOTES PREVIEW =====
document.addEventListener("DOMContentLoaded", () => {
    const previewArea = document.getElementById("previewArea");
    const noteLinks = document.querySelectorAll(".note-link");

    noteLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const filename = link.dataset.filename;
            const type = link.dataset.type.toLowerCase();

            if (!previewArea) return;

            if (type === "txt") {
                fetch(`/uploads/${filename}`)
                    .then(res => res.text())
                    .then(text => {
                        previewArea.innerHTML = `<pre style="white-space: pre-wrap;">${text}</pre>`;
                    })
                    .catch(err => {
                        previewArea.innerHTML = `<p class="text-danger">Failed to load file.</p>`;
                    });
            } else if (type === "pdf") {
                previewArea.innerHTML = `
                    <iframe src="/uploads/${filename}" width="100%" height="400px"></iframe>
                `;
            } else {
                previewArea.innerHTML = `<p class="text-muted">Preview not available for this file type.</p>`;
            }
        });
    });
});
// ===== PROGRESS TRACKER =====
document.addEventListener("DOMContentLoaded", () => {
    const progressTaskList = document.getElementById("progressTaskList");
    const overallProgress = document.getElementById("overallProgress");
    const progressSummary = document.getElementById("progressSummary");

    if (!progressTaskList) return;

    // Load tasks from Planner (localStorage)
    let tasks = JSON.parse(localStorage.getItem("studyTasks")) || [];

    // Load completed status from localStorage
    let completedTasks = JSON.parse(localStorage.getItem("completedTasks")) || {};

    function renderProgress() {
        progressTaskList.innerHTML = "";

        tasks.forEach((task, index) => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";

            const checked = completedTasks[task.subject + task.date + task.time] ? "checked" : "";

            li.innerHTML = `
                <div>
                    <input type="checkbox" class="task-checkbox" data-index="${index}" ${checked}>
                    <strong>${task.subject}</strong> - ${task.date} at ${task.time}
                </div>
            `;

            progressTaskList.appendChild(li);
        });

        updateOverallProgress();
    }

    function updateOverallProgress() {
        const total = tasks.length;
        const done = Object.values(completedTasks).filter(v => v).length;
        const percent = total === 0 ? 0 : Math.round((done / total) * 100);

        overallProgress.style.width = percent + "%";
        overallProgress.textContent = percent + "%";

        progressSummary.textContent = total === 0 ? "No tasks yet." : `${done} of ${total} tasks completed.`;
    }

    // Handle checkbox changes
    progressTaskList.addEventListener("change", (e) => {
        if (e.target.classList.contains("task-checkbox")) {
            const index = e.target.dataset.index;
            const task = tasks[index];
            const key = task.subject + task.date + task.time;

            completedTasks[key] = e.target.checked;
            localStorage.setItem("completedTasks", JSON.stringify(completedTasks));
            updateOverallProgress();
        }
    });

    renderProgress();
});
// SMART STUDY SUGGESTIONS LOGIC
function generateSmartSuggestions() {
    const suggestionBox = document.getElementById("smartSuggestions");
    if (!suggestionBox) return;

    const tasks = JSON.parse(localStorage.getItem("studyTasks")) || [];
    const completedTasks = JSON.parse(localStorage.getItem("completedTasks")) || [];

    suggestionBox.innerHTML = "";

    if (tasks.length === 0) {
        suggestionBox.innerHTML = `
            <li class="list-group-item text-muted">
                Add tasks in Planner to get study suggestions.
            </li>`;
        return;
    }

    const pendingTasks = tasks.filter(
        task => !completedTasks.includes(task.subject + task.date + task.time)
    );

    if (pendingTasks.length === 0) {
        suggestionBox.innerHTML = `
            <li class="list-group-item text-success">
                🎉 Excellent! You are completing all your planned tasks.
            </li>`;
        return;
    }

    pendingTasks.slice(0, 3).forEach(task => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.innerHTML = `
            📌 Focus on <strong>${task.subject}</strong> scheduled on 
            <small>${task.date} at ${task.time}</small>
        `;
        suggestionBox.appendChild(li);
    });
}

// Run suggestions when page loads
document.addEventListener("DOMContentLoaded", generateSmartSuggestions);
// PRIORITY ALERT LOGIC
function checkPriorityAlerts() {
    const alertBox = document.getElementById("priorityAlert");
    if (!alertBox) return;

    const tasks = JSON.parse(localStorage.getItem("studyTasks")) || [];
    const completedTasks = JSON.parse(localStorage.getItem("completedTasks")) || [];

    const today = new Date().toISOString().split("T")[0];

    const pendingToday = tasks.filter(task => {
        const taskId = task.subject + task.date + task.time;
        return task.date === today && !completedTasks.includes(taskId);
    });

    if (pendingToday.length > 0) {
        alertBox.classList.remove("d-none");
        alertBox.innerHTML = `
            ⚠️ You have <strong>${pendingToday.length}</strong> pending task(s) scheduled for today.
        `;
    }
}

// Run alert check on page load
document.addEventListener("DOMContentLoaded", checkPriorityAlerts);
