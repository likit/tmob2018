var ctxActiveResChart = document.getElementById("activeResChart").getContext('2d');
var ctxSchoPerAffilChart = document.getElementById("schoPerAffilChart").getContext('2d');
var ctxPaperPerField = document.getElementById("paperPerField").getContext('2d');

$.when($.getJSON('/analytics/num_abstract_person')).then(function(data) {
    var activeResChart = new Chart(ctxActiveResChart, {
        type: 'pie',
        data: {
            label: "Number of graduated and graduating scholars.",
            datasets: [{
                data: data['data'],
        backgroundColor: ['rgb(255, 99, 132)', 'rgb(124,56,123)'],
        }],
            labels: [
                'Graduating',
                'Graduated'
            ]
        }
    });
});

$.when($.getJSON('/analytics/get_num_active_scholar_studs')).then(function(data) {
    console.log(data)
    var activeScholar = new Chart(ctxSchoPerAffilChart, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                label: 'Inactive',
                data: data['inactives'],
                backgroundColor: data['inactivecolors']
            },
            {
                label: 'Active',
                data: data['actives'],
                backgroundColor: data['activecolors']
            }]
        },
        options: {
            scales: {
                xAxes: [{ stacked: true, ticks: { autoSkip: false }}],
                yAxes: [{ stacked: true }]
            }
        }
    });
});

$.when($.getJSON('/analytics/get_abstract_field')).then(function(data) {
    console.log(data)
    var paperPerField = new Chart(ctxPaperPerField, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                data: data['data'],
                backgroundColor: data['backgroundColors'],
            }],
        },
        options: {
            scales: {
                xAxes: [{ticks: { autoSkip: false }}]
            }
        }
    });
});
