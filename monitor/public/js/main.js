(function worker() {
    var series_size = 100;
    var series_average_fitness = [];

    var margin = {top: 10, right: 50, bottom: 20, left: 50},
        width = 450 - margin.left - margin.right,
        height = 200 - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    var y2 = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    var y2Axis = d3.svg.axis()
        .scale(y2)
        .orient("right");

    var lineAverage = d3.svg.line()
        .x(function (d) {
            return x(d.generation);
        })
        .y(function (d) {
            return y(d.average_fitness);
        });

    var lineDeviation = d3.svg.line()
        .x(function (d) {
            return x(d.generation);
        })
        .y(function (d) {
            return y2(d.std_fitness);
        });

    var svg = d3.select("#graph-container").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y y1 axis")
        .style("fill", "steelblue")
        .call(yAxis);

    svg.append("g")
        .attr("class", "y y2 axis")
        .attr("transform", "translate(" + width + " ,0)")
        .style("fill", "red")
        .call(y2Axis);

    svg.append("path")
        .attr("class", "lineAverage")
        .datum([])
        .attr("d", lineAverage);
    svg.append("path")
        .attr("class", "lineDeviation")
        .datum([])
        .attr("d", lineDeviation);

    (function worker() {
        $.ajax({
            url: '/update',
            success: function (data) {
                // update general props
                for (var a in data) {
                    if (data.hasOwnProperty(a)) {
                        if (['best_fitness', 'average_fitness', 'std_fitness'].indexOf(a) !== -1) {
                            data[a] = Math.round(data[a] * 10000) / 10000;
                        }
                        if (['duration_generation', 'duration_run'].indexOf(a) !== -1) {
                            if (data[a]>60) {
                                var m = Math.round(data[a]/60);
                                var s = data[a]%60
                                data[a] = m+'m '+s+'s';
                            } else {
                                data[a] += 's';
                            }
                        }
                        $('#' + a).text(data[a]);
                    }
                }

                if (data.genomes.length) {
                    // images
                    var images = $('#images').html('');
                    var imageTemplate = $('#image-template div');
                    var image;
                    data.genomes.sort(function (a, b) {
                        return parseFloat(a.fitness) - parseFloat(b.fitness);
                    });
                    for (var i = 0, n = 12; i < n; i++) {
                        if (data.genomes[i]) {
                            image = imageTemplate.clone();
                            image.find('img').attr('src', data.genomes[i].pngPath);
                            if (data.genomes[i].serial == data.best_genome) {
                                image.find('img').addClass('bestGenome');
                            }
                            images.append(image);
                        }
                    }
                }

                if (data.generation) {
                    if (series_average_fitness.length == 0 || data.generation != series_average_fitness[series_average_fitness.length - 1].generation) {
                        series_average_fitness.push({
                            generation: parseInt(data.generation),
                            average_fitness: data.average_fitness,
                            std_fitness: parseFloat(data.std_fitness),
                        });
                    }
                    if (series_average_fitness.length > series_size) {
                        series_average_fitness.shift();
                    }

                    x.domain(d3.extent(series_average_fitness, function (d) {
                        return d.generation;
                    }));
                    y.domain(d3.extent(series_average_fitness, function (d) {
                        return d.average_fitness;
                    }));
                    y2.domain(d3.extent(series_average_fitness, function (d) {
                        return d.std_fitness;
                    }));

                    svg.transition();
                    svg.select(".lineAverage")
                        .datum(series_average_fitness)
                        .attr("d", lineAverage);
                    svg.select(".lineDeviation")
                        .datum(series_average_fitness)
                        .attr("d", lineDeviation);
                    svg.select(".x.axis")
                        .call(xAxis);
                    svg.select(".y1.axis")
                        .call(yAxis);
                    svg.select(".y2.axis")
                        .call(y2Axis);
                }
            },
            complete: function () {
                // Schedule the next request when the current one's complete
                setTimeout(worker, 2000);
            }
        });
    })();
})();