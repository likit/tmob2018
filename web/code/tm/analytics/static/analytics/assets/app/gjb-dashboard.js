var ctxStatusChart = document.getElementById("statusChart").getContext('2d');

$.when($.getJSON('/analytics/count_gjb_by_status')).then(function(data) {
    var activeResChart = new Chart(ctxStatusChart, {
        type: 'pie',
        data: {
            label: "Number of graduated and graduating scholars.",
            datasets: [{
                data: data['data'],
                backgroundColor: ['rgb(199, 0, 57)', 'rgb(100,116,164)'],
            }],
            labels: [
                'โครงการยังไม่สิ้นสุดอย่างสมบูรณ์',
                'โครงการสิ้นสุดแล้ว'
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
});

var ctxStatusAffilChart = document.getElementById("statusAffilChart").getContext('2d');
$.when($.getJSON('/analytics/count_gjb_by_status_affil')).then(function(data) {
    var activeScholar = new Chart(ctxStatusAffilChart, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                label: 'โครงการยังไม่สิ้นสุดสมบูรณ์',
                data: data['inactives'],
                backgroundColor: data['inactivecolors']
            },
                {
                    label: 'โครงการสิ้นสุดแล้ว',
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

var ctxActiveChart = document.getElementById("activeChart").getContext('2d');
$.when($.getJSON('/analytics/count_active_gjb_researcher')).then(function(data) {
    var activeScholar = new Chart(ctxActiveChart, {
        type: 'bar',
        data: {
            labels: data['labels'],
            datasets: [{
                label: 'ไม่มีผลงานวิจัยตั้งแต่ปี 2013-ปัจจุบัน',
                data: data['inactives'],
                backgroundColor: data['inactivecolors']
            },
                {
                    label: 'มีผลงานวิจัยในปี 2013-ปัจจุบัน',
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

var ctxFieldRadarChart = document.getElementById("fieldRadarChart").getContext('2d');
$.when($.getJSON('/analytics/count_gjb_pub_by_field')).then(function(data) {
    var activeScholar = new Chart(ctxFieldRadarChart, {
        type: 'radar',
        data: {
            labels: data['labels'],
            datasets: [{
                data: data['gjb_counts'],
                label: 'GJB',
                fill: false,
                borderColor: 'rgb(199, 0, 57)'
            },
                {
                    data: data['sc_counts'],
                    label: 'SCI',
                    fill: false,
                    borderColor: 'rgb(100,116,164)'
                }]
        },
        options: {
            scales: {
            }
        }
    });
});
