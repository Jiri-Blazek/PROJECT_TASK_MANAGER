const cpus_chart = document.getElementById("cpus_chart");

max_cpus = [100, 100, 100, 100];
used_cpus = [65, 59, 80, 81];
rest_cpus = max_cpus.map((x, i) => x - used_cpus[i]);

const labels_cpus = ['Word', 'Powerpoint', 'Excel', 'Total'];

const data_used_cpus = {
    labels: labels_cpus,
    datasets: [
        {
            label: 'Current used CPUs',
            data: rest_cpus,
            backgroundColor: '#FFB70F',

        },
        {
            label: 'Remaining CPUs',
            data: used_cpus,
            borderColor: ' rgba(54, 162, 235, 0.2)',
        },
    ]
};


const cpus_chart_config = {
    type: 'bar',
    data: data_used_cpus,
    options: {
        plugins: {
            title: {
                display: true,
                text: 'Used CPUs',
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

