document.addEventListener("DOMContentLoaded", () => {
    const historyButtons = document.querySelectorAll(".getHis");
    const modal = document.getElementById("historyModal");
    const closeModal = document.getElementById("closeModal");

    historyButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const taskId = btn.dataset.taskId;
            showHistoryModal(taskId);
        });
    });

    closeModal.addEventListener("click", () => modal.classList.remove("is-active"));
    modal.querySelector(".modal-background").addEventListener("click", () => modal.classList.remove("is-active"));

    function showHistoryModal(taskId) {
        modal.classList.add("is-active");

        const memoryLabels = JSON.parse(document.getElementById("memory-labels-data").textContent);
        const usedMemory = JSON.parse(document.getElementById("used-memory-data").textContent);
        const cpuLabels = JSON.parse(document.getElementById("cpu-labels-data").textContent);
        const usedCpu = JSON.parse(document.getElementById("used-cpus-data").textContent);

        renderCharts(memoryLabels, usedMemory, cpuLabels, usedCpu);
    }

    function renderCharts(memoryLabels, usedMemory, cpuLabels, usedCpu) {
        const MAX_MEMORY = 1000;
        const restMemory = usedMemory.map(v => MAX_MEMORY - v);

        const MAX_CPU = 100;
        const restCpu = usedCpu.map(v => MAX_CPU - v);

        const memoryChartEl = document.getElementById("memory_chart_modal");
        const cpuChartEl = document.getElementById("cpu_chart_modal");

        if (memoryChartEl.chart) memoryChartEl.chart.destroy();
        if (cpuChartEl.chart) cpuChartEl.chart.destroy();

        memoryChartEl.chart = new Chart(memoryChartEl, {
            type: 'bar',
            data: {
                labels: memoryLabels,
                datasets: [
                    { label: 'Used memory', data: usedMemory, backgroundColor: '#FFB70F' },
                    { label: 'Remaining memory', data: restMemory, backgroundColor: '#36A2EB' }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Used memory [MB]', font: { size: 18, weight: 'bold' } } }, scales: { x: { stacked: true }, y: { stacked: true } } }
        });

        cpuChartEl.chart = new Chart(cpuChartEl, {
            type: 'bar',
            data: {
                labels: cpuLabels,
                datasets: [
                    { label: 'Used CPU', data: usedCpu, backgroundColor: '#FFB70F' },
                    { label: 'Remaining CPU', data: restCpu, backgroundColor: '#36A2EB' }
                ]
            },
            options: { responsive: true, plugins: { title: { display: true, text: 'Used CPU [%]', font: { size: 18, weight: 'bold' } } }, scales: { x: { stacked: true }, y: { stacked: true } } }
        });
    }
});