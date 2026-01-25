const memory_chart = document.getElementById("memory_chart");

max_memory = [220, 220, 220, 220];
used_memory = [65, 59, 80, 81];
rest_memory = max_memory.map((x, i) => x - used_memory[i]);

const labels_memory = ['Word', 'Powerpoint', 'Exce', 'Total'];

const data_used_memory = {
    labels: labels_memory,
    datasets: [
        {
            label: 'Current used memory',
            data: rest_memory,
            backgroundColor: '#FFB70F',

        },
        {
            label: 'Remaining memory',
            data: used_memory,
            borderColor: ' rgba(54, 162, 235, 0.2)',
        },
    ]
};


const memory_chart_config = {
    type: 'bar',
    data: data_used_memory,
    options: {
        plugins: {
            title: {
                display: true,
                text: 'Used memory',
                font: {
                    size: 18,
                    weight: 'bold'
                }
            },
        },
        responsive: true,
        scales: {
            x: {
                stacked: true,
            },
            y: {
                stacked: true
            }
        }
    }
};

