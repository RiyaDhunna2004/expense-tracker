function getThemeColors() {
  const isLightMode = document.body.classList.contains("light-mode");

  return {
    textColor: isLightMode ? "#111" : "#ffffff",
    gridColor: isLightMode
      ? "rgba(0,0,0,0.15)"
      : "rgba(255,255,255,0.15)",
  };
}

async function loadCategoryChart() {
  const { textColor, gridColor } = getThemeColors();

  const response = await fetch("/analytics/category");
  const data = await response.json();

  const labels = Object.keys(data);
  const values = Object.values(data);

  const ctx = document.getElementById("categoryChart").getContext("2d");

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: [
            "#ff4757",
            "#3742fa",
            "#2ed573",
            "#ffa502",
            "#e056fd",
            "#00d2d3",
          ],
          borderColor: "#ffffff",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColor,
          },
        },
      },
    },
  });
}

async function loadMonthlyChart() {
  const { textColor, gridColor } = getThemeColors();

  const response = await fetch("/analytics/monthly");
  const data = await response.json();

  const labels = Object.keys(data);
  const values = Object.values(data);

  const ctx = document.getElementById("monthlyChart").getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Expenses",
          data: values,
          borderColor: "#ff4757",
          backgroundColor: "rgba(255,71,87,0.2)",
          borderWidth: 3,
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColor,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: textColor,
          },
          grid: {
            color: gridColor,
          },
        },
        y: {
          ticks: {
            color: textColor,
          },
          grid: {
            color: gridColor,
          },
        },
      },
    },
  });
}

async function loadIncomeChart() {
  const { textColor, gridColor } = getThemeColors();

  const response = await fetch("/analytics/income");
  const data = await response.json();

  const labels = Object.keys(data);
  const values = Object.values(data);

  const ctx = document.getElementById("incomeChart").getContext("2d");

  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Monthly Income",
          data: values,
          borderColor: "#2ed573",
          backgroundColor: "rgba(46,213,115,0.2)",
          borderWidth: 3,
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColor,
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: textColor,
          },
          grid: {
            color: gridColor,
          },
        },
        y: {
          ticks: {
            color: textColor,
          },
          grid: {
            color: gridColor,
          },
        },
      },
    },
  });
}

window.onload = function () {
  if (document.getElementById("categoryChart")) loadCategoryChart();
  if (document.getElementById("monthlyChart")) loadMonthlyChart();
  if (document.getElementById("incomeChart")) loadIncomeChart();
};