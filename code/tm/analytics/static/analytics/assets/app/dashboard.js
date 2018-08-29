var ctxActiveResChart = document.getElementById("activeResChart").getContext('2d');
var ctxSchoPerAffilChart = document.getElementById("schoPerAffilChart").getContext('2d');
var ctxPaperPerField = document.getElementById("paperPerField").getContext('2d');
var ctxResearcherPerField = document.getElementById("researcherPerField").getContext('2d');

$.when($.getJSON('/analytics/num_abstract_person')).then(function(data) {
    var activeResChart = new Chart(ctxActiveResChart, {
        type: 'pie',
        data: {
            label: "Number of graduated and graduating scholars.",
            datasets: [{
                data: data['data'],
        backgroundColor: ['rgb(199, 0, 57)', 'rgb(100,116,164)'],
        }],
            labels: [
                'กำลังศึกษาอยู่',
                'จบการศึกษาแล้ว'
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
});

$.when($.getJSON('/analytics/get_num_active_scholar_studs')).then(function(data) {
    var activeScholar = new Chart(ctxSchoPerAffilChart, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                label: 'ยังไม่มีผลงานวิจัยในรอบห้าปี',
                data: data['inactives'],
                backgroundColor: data['inactivecolors']
            },
            {
                label: 'มีผลงานวิจัยในรอบห้าปี',
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
    var paperPerField = new Chart(ctxPaperPerField, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                data: data['data'],
                label: 'จำนวนผลงาน',
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

$.when($.getJSON('/analytics/get_researcher_by_field')).then(function(data) {
    var paperPerField = new Chart(ctxResearcherPerField, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                label: 'ยังไม่มีผลงานวิจัยในรอบห้าปี',
                data: data['inactives'],
                backgroundColor: data['inactivecolors']
            },
            {
                label: 'มีผลงานวิจัยในรอบห้าปี',
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
