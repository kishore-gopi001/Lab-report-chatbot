// =====================================================
// DASHBOARD SUMMARY COUNTS
// =====================================================
async function loadSummary() {
    const res = await fetch("/reports/summary");
    const data = await res.json();

    let total = 0, normal = 0, abnormal = 0, critical = 0, unknown = 0;

    data.forEach(row => {
        total += row.count;
        if (row.status === "NORMAL") normal = row.count;
        else if (row.status === "ABNORMAL") abnormal = row.count;
        else if (row.status === "CRITICAL") critical = row.count;
        else unknown += row.count;
    });

    document.getElementById("totalLabs").innerText = total;
    document.getElementById("normalCount").innerText = normal;
    document.getElementById("abnormalCount").innerText = abnormal;
    document.getElementById("criticalCount").innerText = critical;
    document.getElementById("unknownCount").innerText = unknown;
}

// =====================================================
// BAR CHART – AFFECTED TESTS
// =====================================================
async function loadLabChart() {
    const res = await fetch("/reports/by-lab");
    const data = await res.json();

    const labMap = {};
    data.forEach(row => {
        labMap[row.test_name] = (labMap[row.test_name] || 0) + row.patient_count;
    });

    new Chart(document.getElementById("labChart"), {
        type: "bar",
        data: {
            labels: Object.keys(labMap),
            datasets: [{
                data: Object.values(labMap),
                backgroundColor: "#1f3c88"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

// =====================================================
// PIE CHART – GENDER DISTRIBUTION
// =====================================================
async function loadGenderChart() {
    const res = await fetch("/reports/by-gender");
    const data = await res.json();

    const genderMap = {};
    data.forEach(row => {
        genderMap[row.gender] = (genderMap[row.gender] || 0) + row.patient_count;
    });

    new Chart(document.getElementById("genderChart"), {
        type: "pie",
        data: {
            labels: Object.keys(genderMap),
            datasets: [{
                data: Object.values(genderMap),
                backgroundColor: ["#36a2eb", "#ff6384", "#cfbebe"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// =====================================================
// DOUGHNUT CHART – STATUS OVERVIEW
// =====================================================
async function loadStatusChart() {
    const res = await fetch("/reports/summary");
    const data = await res.json();

    new Chart(document.getElementById("statusChart"), {
        type: "doughnut",
        data: {
            labels: data.map(r => r.status),
            datasets: [{
                data: data.map(r => r.count),
                backgroundColor: ["#4caf50", "#ff9800", "#f44336", "#9e9e9e"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } }
        }
    });
}

// =====================================================
// TABLE – TOP AFFECTED TESTS
// =====================================================
async function loadTopTestsTable() {
    const res = await fetch("/reports/by-lab");
    const data = await res.json();

    const tbody = document.querySelector("#topTestsTable tbody");
    tbody.innerHTML = "";

    data.slice(0, 10).forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.test_name}</td>
            <td>${row.status}</td>
            <td>${row.patient_count}</td>
        `;
        tbody.appendChild(tr);
    });
}

// =====================================================
// ALERT PANEL – UNREVIEWED CRITICAL
// =====================================================
async function loadCriticalAlerts() {
    const res = await fetch("/reports/unreviewed-critical");
    const data = await res.json();

    const alertBox = document.getElementById("criticalAlerts");
    alertBox.innerHTML = "";

    if (data.length === 0) {
        alertBox.innerHTML = "<li>No pending critical alerts 🎉</li>";
        return;
    }

    data.slice(0, 5).forEach(row => {
        const li = document.createElement("li");
        li.textContent = `Subject ${row.subject_id} | ${row.test_name}: ${row.value} ${row.unit}`;
        alertBox.appendChild(li);
    });
}

// =====================================================
// INITIAL DASHBOARD LOAD
// =====================================================
loadSummary();
loadLabChart();
loadGenderChart();
loadStatusChart();
loadTopTestsTable();
loadCriticalAlerts();

// =====================================================
// CHATBOT LOGIC (NUMERIC-SAFE)
// =====================================================
const toggleBtn = document.getElementById("chatbotToggle");
const chatbotWindow = document.getElementById("chatbotWindow");
const closeBtn = document.getElementById("chatbotClose");
const sendBtn = document.getElementById("sendMessage");

const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const aiSummaryBox = document.getElementById("aiSummary");
const subjectInput = document.getElementById("subjectInput");

let activeSubjectId = null;

// Open / Close
toggleBtn.onclick = () => chatbotWindow.classList.remove("hidden");
closeBtn.onclick = () => chatbotWindow.classList.add("hidden");

// Subject ID entered
subjectInput.addEventListener("change", async () => {
    activeSubjectId = subjectInput.value.trim();
    chatMessages.innerHTML = "";

    if (!activeSubjectId) return;

    aiSummaryBox.innerHTML = "<p>⏳ Generating AI summary…</p>";

    const poll = setInterval(async () => {
        const res = await fetch(`/chat/patient/${activeSubjectId}/ai-summary`);
        const data = await res.json();

        if (data.summary) {
            aiSummaryBox.innerHTML = `
                <strong>🧠 AI Clinical Summary</strong>
                <p style="margin-top:8px;">${data.summary}</p>
                <small>${data.disclaimer}</small>
            `;
            clearInterval(poll);
        }
    }, 2000);
});

// Send chat message
sendBtn.onclick = async () => {
    const question = chatInput.value.trim();
    if (!question || !activeSubjectId) return;

    chatMessages.innerHTML += `<div class="msg user">${question}</div>`;
    chatInput.value = "";

    const res = await fetch(`/chat/patient/${activeSubjectId}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    });

    const data = await res.json();

    chatMessages.innerHTML += `
        <div class="msg bot">
            <strong>📋 Response</strong>
            <p style="margin-top:6px;">${data.answer}</p>
            <small>Confidence: ${(data.confidence_score * 100).toFixed(0)}%</small>
        </div>
    `;

    chatMessages.scrollTop = chatMessages.scrollHeight;
};
