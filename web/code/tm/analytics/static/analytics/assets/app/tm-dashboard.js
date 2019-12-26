var ctxScholarshipRatio = document.getElementById("scholarshipRatio").getContext('2d');
var ctxSchoPerAffilChart = document.getElementById("schoPerAffilChart").getContext('2d');
var ctxSchoTmActivenessChart = document.getElementById("schoTmActivenessChart").getContext('2d');

$.when($.getJSON('/analytics/get_scholar_joined_tm_ratio')).then(function(data) {
    var activeResChart = new Chart(ctxScholarshipRatio, {
        type: 'pie',
        data: {
            label: "Number of scholars.",
            datasets: [{
                data: data['data'],
                backgroundColor: ['rgb(199, 0, 57)', 'rgb(100,116,164)'],
            }],
            labels: [
                'นักเรียนทุนก.วิทย์',
                'ทั่วไป'
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
});

$.when($.getJSON('/analytics/get_num_active_scholar_tm')).then(function(data) {
    var activeScholar = new Chart(ctxSchoPerAffilChart, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                label: 'ยังไม่เข้าร่วมโครงการฯ',
                data: data['inactives'],
                backgroundColor: data['inactivecolors']
            },
                {
                    label: 'เข้าร่วมโครงการฯ',
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

$.when($.getJSON('/analytics/get_activeness_scholar_tm')).then(function(data) {
    var activeScholar = new Chart(ctxSchoTmActivenessChart, {
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


