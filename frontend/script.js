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
    const res = await fetch("https://smart-task-analyzer-g3nf.onrender.com/api/tasks/analyze/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error("Server error: " + res.status);
    }

    const data = await res.json();
    displayResults(data.tasks || []);
    
  } catch (err) {
    console.error(err);
    alert("Failed to call API. Is server running?");
  }
}
