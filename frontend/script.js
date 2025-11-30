async function analyzeTasks() {
  const raw = document.getElementById('taskInput').value;
  const strategy = document.getElementById('strategy').value;
  let tasks;
  try {
    tasks = JSON.parse(raw);
    if (!Array.isArray(tasks)) throw "Expecting array";
  } catch (err) {
    alert("Invalid JSON. Provide an array of tasks.");
    return;
  }
  const payload = { tasks, strategy };
  try {
    const res = await fetch("https://smart-task-analyzer-g3nf.onrender.com/api/tasks/suggest/", {


      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    displayResults(data.tasks || []);
  } catch (err) {
    console.error(err);
    alert("Failed to call API. Is server running?");
  }
}

function displayResults(tasks) {
  const root = document.getElementById('results');
  root.innerHTML = '';
  tasks.forEach(t => {
    const card = document.createElement('div');
    card.className = 'task-card ' + priorityClass(t.score);
    card.innerHTML = `<h3>${t.title}</h3>
      <p><b>Score:</b> ${t.score}</p>
      <p><b>Due:</b> ${t.due_date || '—'}</p>
      <p><b>Importance:</b> ${t.importance}</p>
      <p><b>Effort (hrs):</b> ${t.estimated_hours}</p>
      <p><b>Why:</b> ${t.explanation || ''}</p>`;
    root.appendChild(card);
  });
}

function priorityClass(score) {
  if (score >= 200) return 'high';
  if (score >= 80) return 'medium';
  return 'low';
}
