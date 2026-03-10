console.log("✅ habit.js connected successfully!");

document.addEventListener('DOMContentLoaded', function () {
  const habitForm = document.getElementById('habitForm');
  const habitInput = document.getElementById('habitInput');
  const habitTableBody = document.getElementById('habitTableBody');
  const weeklyChartCanvas = document.getElementById('weeklyChart');
  let weeklyChart;

  // ✅ Load everything on page load
  loadHabits();
  loadWeeklyReport();

  // ✅ Add new habit
  habitForm.addEventListener('submit', async function (event) {
    event.preventDefault();
    const habit = habitInput.value.trim();
    if (!habit) return alert('Please enter a habit');

    try {
      const response = await fetch('/add_habit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ habit }),
      });

      const data = await response.json();
      alert(data.message || data.error);
      habitInput.value = '';
      await loadHabits();
      await loadWeeklyReport();
    } catch (error) {
      console.error("Error adding habit:", error);
      alert("Something went wrong while adding the habit!");
    }
  });

  // ✅ Load habits table
  async function loadHabits() {
    const response = await fetch('/get_habits');
    const habits = await response.json();
    habitTableBody.innerHTML = '';

    habits.forEach(habit => {
      const row = document.createElement('tr');
      const statusColor = habit.status === "Done" ? "style='color:green; font-weight:bold;'" : "";
      row.innerHTML = `
        <td>${habit.habit}</td>
        <td ${statusColor}>${habit.status}</td>
        <td><button class="mark-done" data-id="${habit.id}">Mark as Done</button></td>
      `;
      habitTableBody.appendChild(row);
    });

    // Attach listeners after rendering
    document.querySelectorAll('.mark-done').forEach(button => {
      button.addEventListener('click', async (e) => {
        const habitId = e.target.getAttribute('data-id');
        const res = await fetch(`/mark_done/${habitId}`, { method: 'POST' });
        if (res.ok) {
          await loadHabits();
          await loadWeeklyReport();
        }
      });
    });
  }

  // ✅ Load weekly progress graph
  async function loadWeeklyReport() {
    try {
      const response = await fetch('/weekly_report');
      const data = await response.json();

      const labels = data.map(d => d.date);
      const values = data.map(d => d.completion);

      if (weeklyChart) weeklyChart.destroy();

      weeklyChart = new Chart(weeklyChartCanvas, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Completion %',
            data: values,
            backgroundColor: '#00b4d8',
          }],
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              title: { display: true, text: 'Completion (%)' }
            },
            x: {
              title: { display: true, text: 'Days of the Week' }
            }
          }
        }
      });
    } catch (error) {
      console.error("Error loading weekly report:", error);
    }
  }
});