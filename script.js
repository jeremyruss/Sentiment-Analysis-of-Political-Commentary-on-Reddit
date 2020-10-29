var labels = [];
var data = [];

function init() {

    fetch('./subreddit_data.json')
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {

            var i;

            var bubbledata = [];
            var bardata = [];
            var piedata = [];

            var dataframe = data;

            console.log(dataframe)

            var relatedSubreddits = dataframe['all'].related;
            var relatedSubredditLabels = Object.keys(relatedSubreddits);

            delete dataframe['all'];
            var subredditLabels = Object.keys(dataframe);

            for (var name in dataframe) {
                var obj = {
                    x: dataframe[name].sentiment,
                    y: dataframe[name].polarity,
                    r: Math.sqrt((dataframe[name].size) / Math.PI) / 12
                }
                bubbledata.push(obj);
                piedata.push(dataframe[name].size);
            }

            bardata = Object.values(relatedSubreddits);

            bubblechart.data.labels = subredditLabels;
            barchart.data.labels = relatedSubredditLabels;
            piechart.data.labels = subredditLabels;

            bubblechart.data.datasets[0].data = bubbledata;
            barchart.data.datasets[0].data = bardata;
            piechart.data.datasets[0].data = piedata;

            generateColour();

            //barchart.options.scales.xAxes[0].ticks.suggestedMax = Math.max.apply(Math, bardata) + 1;

            bubblechart.update()
            barchart.update()
            piechart.update()

        })

}

function clicked(subreddit, clickedElementIndex) {

    fetch('./subreddit_data.json')
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {

            var dataframe = data;

            var relatedSubreddits = dataframe[subreddit].related;
            var relatedSubredditLabels = Object.keys(relatedSubreddits);
            var bardata = Object.values(relatedSubreddits);

            barchart.data.labels = relatedSubredditLabels;
            barchart.data.datasets[0].data = bardata;

            var x = dataframe[subreddit].sentiment;

            if (x > 0) {
                barchart.data.datasets[0].backgroundColor = 'rgb(190, 0, 0, 0.8)';
                bubblechart.data.datasets[0].backgroundColor[clickedElementIndex] = 'rgb(190, 0, 0, 0.8)';
                bubblechart.options.elements.point.hoverBackgroundColor[clickedElementIndex] = 'rgb(190, 0, 0, 0.8)';
            } else {
                barchart.data.datasets[0].backgroundColor = 'rgb(0, 20, 190, 0.8)';
                bubblechart.data.datasets[0].backgroundColor[clickedElementIndex] = 'rgb(0, 20, 190, 0.8)';
                bubblechart.options.elements.point.hoverBackgroundColor[clickedElementIndex] = 'rgb(0, 20, 190, 0.8)';
            }

            //barchart.options.scales.xAxes[0].ticks.suggestedMax = Math.max.apply(Math, bardata) + 1;

            bubblechart.update()
            barchart.update()
            piechart.update()

        })

}

function generateColour() {
    var colour = [];
    var hoverColour = [];
    var barColours = [];
    var data = bubblechart.data.datasets[0].data;
    var i;

    for (i = 0; i < data.length; i++) {
        if (data[i].x < 0) {
            colour.push('rgb(0, 20, 190, 0.6)')
            hoverColour.push('rgb(0, 20, 190, 0.5)')
        } else {
            colour.push('rgb(190, 0, 0, 0.6)')
            hoverColour.push('rgb(190, 0, 0, 0.5)')
        }
    }

    bubblechart.data.datasets[0].backgroundColor = colour;
    bubblechart.data.datasets[0].borderColor = colour;
    bubblechart.options.elements.point.hoverBackgroundColor = hoverColour;

    var length = barchart.data.datasets[0].data.length;
    for (i = 0; i < length; i++) {
        if (i % 2 == 0) {
            barColours.push('rgb(0, 20, 190, 0.6)');
        } else {
            barColours.push('rgb(190, 0, 0, 0.6)');
        }
    }

    barchart.data.datasets[0].backgroundColor = barColours;

    piechart.data.datasets[0].backgroundColor = colour;
    piechart.options.elements.point.hoverBackgroundColor = hoverColour;

}

// Chartjs scatter plot configuration

var ctx = document.getElementById('bubble').getContext('2d');

var bubblechart = new Chart(ctx, {

    type: 'bubble',

    data: {
        labels: labels,
        datasets: [{
            data: data
        }]
    },

    options: {
        aspectRatio: 1,
        legend: false,
        tooltips: false,
        scales: {
            yAxes: [{
                display: true,
                ticks: {
                    suggestedMin: 0,
                    suggestedMax: 0.2,
                    stepSize: 0.025
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Polarity'
                }
            }],
            xAxes: [{
                ticks: {
                    suggestedMin: -0.5,
                    suggestedMax: 0.4,
                    stepSize: 0.1
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Sentiment'
                }
            }]
        },
        elements: {
            point: {
                borderWidth: 0,
                hoverRadius: 0,
                hoverBorderWidth: 0
            }
        },
        tooltips: {
            callbacks: {
                label: function (tooltipItem, data) {
                    var label = 'r/' + data.labels[tooltipItem.index];
                    return label;
                }
            }
        },
        layout: {
            padding: {
                top: 25,
                right: 25,
                left: 25,
                bottom: 25
            }
        },
        onClick: function (e) {
            generateColour();
            var activePoints = bubblechart.getElementsAtEvent(e);
            if (activePoints.length > 0) {
                var clickedElementIndex = activePoints[0]["_index"];
                var label = bubblechart.data.labels[clickedElementIndex];
                clicked(label, clickedElementIndex);
            } else {
                init();
            }
            console.log(label)
        }
    }

});

// Chartjs bar chart configuration

var ctx = document.getElementById('bar').getContext('2d');

var barchart = new Chart(ctx, {

    type: 'horizontalBar',

    data: {

        labels: labels,
        datasets: [{
            backgroundColor: 'transparent',
            borderColor: '#000',
            data: data
        }]

    },

    options: {
        maintainAspectRatio: false,
        legend: false,
        tooltips: false,
        scales: {
            xAxes: [{
                ticks: {
                    suggestedMin: 0,
                    suggestedMax: 0,
                    display: false
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Popularity'
                }
            }],
            yAxes: [{
                afterFit: function (scaleInstance) {
                    scaleInstance.width = 160;
                }
            }]
        }
    }

});

// Chartjs pie chart configuration

var ctx = document.getElementById('pie').getContext('2d');

var piechart = new Chart(ctx, {

    type: 'doughnut',

    data: {

        labels: labels,
        datasets: [{
            borderColor: 'white',
            hoverBorderColor: 'white',
            borderWidth: 5,
            hoverBorderWidth: 5,
            data: data
        }]

    },

    options: {
        maintainAspectRatio: false,
        legend: {
            position: 'right',
            align: 'center'
        },
        tooltips: false,
        layout: {
            padding: {
                left: 50
            }
        },
        onClick: function (e) {
            generateColour();
            var activePoints = piechart.getElementsAtEvent(e);
            if (activePoints.length > 0) {
                var clickedElementIndex = activePoints[0]["_index"];
                var label = piechart.data.labels[clickedElementIndex];
                clicked(label, clickedElementIndex);
            } else {
                init();
            }
            console.log(label)
        }
    }

});

init();