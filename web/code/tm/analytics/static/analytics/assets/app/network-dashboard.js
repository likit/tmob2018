$.when($.getJSON('/analytics/get_tm_researchers_graph_data')).then(function(data) {
    var container = document.getElementById('mynetwork');
    var network = null;
    var dataset = {
        nodes: data.nodes,
        edges: data.edges
    }
    var options = {
        nodes: {
            shape: 'dot',
            scaling:{
                label: {
                    min:8,
                    max:20
                }
            }
        },
        layout: {
            improvedLayout: false
        }
    };
    network = new vis.Network(container, dataset, options);
});
