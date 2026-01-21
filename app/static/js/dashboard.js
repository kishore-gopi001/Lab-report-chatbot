async function loadSummary() {
    const res = await fetch("/reports/summary");
    const data = await res.json();

    let total = 0, abnormal = 0, critical = 0;

    data.forEach(row => {
        total += row.count;
        if (row.status === "ABNORMAL") abnormal = row.count;
        if (row.status === "CRITICAL") critical = row.count;
    });

    document.getElementById("totalLabs").innerText = total;
    document.getElementById("abnormalCount").innerText = abnormal;
    document.getElementById("criticalCount").innerText = critical;
}

async function loadLabChart() {
    const res = await fetch("/reports/by-lab");
    const data = await res.json();

    const labMap = {};

    data.forEach(row => {
        if (!labMap[row.test_name]) {
            labMap[row.test_name] = 0;
        }
        labMap[row.test_name] += row.patient_count;
    });

    new Chart(document.getElementById("labChart"), {
        type: "bar",
        data: {
            labels: Object.keys(labMap),
            datasets: [{
                label: "Patients affected",
                data: Object.values(labMap),
                backgroundColor: "#1f3c88"
            }]
        }
    });
}

async function loadGenderChart() {
    const res = await fetch("/reports/by-gender");
    const data = await res.json();

    const genderMap = {};

    data.forEach(row => {
        if (!genderMap[row.gender]) {
            genderMap[row.gender] = 0;
        }
        genderMap[row.gender] += row.patient_count;
    });

    new Chart(document.getElementById("genderChart"), {
        type: "pie",
        data: {
            labels: Object.keys(genderMap),
            datasets: [{
                data: Object.values(genderMap),
                backgroundColor: ["#36a2eb", "#ff6384"]
            }]
        }
    });
}

async function askChatbot() {
    const subjectId = document.getElementById("subjectInput").value;
    const res = await fetch(`/chat/patient/${subjectId}/abnormal`);
    const data = await res.json();

    document.getElementById("chatbotResponse").innerText =
        JSON.stringify(data, null, 2);
}

loadSummary();
loadLabChart();
loadGenderChart();
