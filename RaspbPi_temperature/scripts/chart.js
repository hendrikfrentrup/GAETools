$(document).ready(function() {

    var options = {
        chart: {
            renderTo: 'container',
            type: 'line'
        },
        title: {
            text: 'Temperature Readings'
        },
        series: [{
            name: 'Temperature',
            data: []
        }],
        xAxis: {
            title: {
                text: 'Reading #'
            },
            tickInterval: 1
        },
        yAxis: {
            title: {
                text: 'Temperature [C]'
            },
            tickInterval: 5
        }
    };
    
    $.getJSON('/query', function(data) {
        options.series[0].data = data;
        var chart = new Highcharts.Chart(options);
    });
    

});
