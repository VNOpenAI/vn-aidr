window.probaChartData = {
    labels: ['Pleural Effusion', 'Atelectasis', 'Consolidation', 'Edema', 'Cardiomegaly'],
    datasets: [{
        label: "probability",
        backgroundColor: Chart.helpers.color("#04d6b3").alpha(0.5).rgbString(),
        borderColor: "#04d6b3",
        borderWidth: 2,
        scaleStepWidth: 1,
        data: [0,0,0,0,0]
    }]

};

window.onload = function () {
    var ctx = document.getElementById('proba-chart').getContext('2d');
    console.log(ctx);
    window.probaChart = new Chart(ctx, {
        type: 'horizontalBar',
        data: window.probaChartData,
        options: {
            // Elements options apply to all of the options unless overridden in a dataset
            // In this case, we are setting the border of each horizontal bar to be 2px wide
            elements: {
                rectangle: {
                    borderWidth: 2,
                }
            },
            responsive: true,
            legend: false,
            scales: {
                yAxes: [{
                    ticks: {
                        fontColor: "#04d6b3",
                        fontSize: 14,
                        stepSize: 10
                    },
                    gridLines: {
                        color: '#001927',
                        lineWidth: 1
                    },
                    barPercentage: 0.9
                }],
                xAxes: [{
                    ticks: {
                        fontColor: "#04d6b3",
                        fontSize: 14,
                        stepSize: 20,
                        beginAtZero: true,
                        max: 100,
                    },
                    gridLines: {
                        color: '#001927',
                        lineWidth: 1
                      }
                }]
            },
            title: false
        }
    });

};