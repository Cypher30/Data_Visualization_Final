import Chart from "./chart.js";

d3.csv('./data/Radar/Radar_1.csv', function (d) {
    return {
        subject: d.type,
        person1: +d.a,
        person2: +d.b,
        person3: +d.c,
        person4: +d.d
    };
}).then(function (data) {
    /* ----------------------------配置参数------------------------  */
    const chart = new Chart();
    const config = {
        margins: { top: 0, left: 80, bottom: 0, right: 80 },
        textColor: 'black',
        title: 'Alldrik',
        radius: 100,
        animateDuration: 1000,
        tickNum: 5,
        axisfillColor: ['white', '#ddd'],
        axisStrokeColor: 'yellow',
        pointsColor: 'white',
        pointsSize: 3
    }

    chart.margins(config.margins);

    /* ----------------------------尺度转换------------------------  */
    chart.scaleRadius = d3.scaleLinear()
        .domain([0, 100])
        .range([0, config.radius])

    /* ----------------------------渲染坐标轴------------------------  */
    chart.renderAxes = function () {

        // ----渲染背景多边形-----
        const points = getPolygonPoints(data.length, config.radius, config.tickNum);

        const axes = chart.body().append('g')
            .attr('class', 'axes')
            .attr('transform', 'translate(' + chart.getBodyWidth() / 2 + ',' + chart.getBodyHeight() / 2 + ')')
            .selectAll('axis')
            .data(points);

        axes.enter()
            .append('polygon')
            .attr('class', 'axis')
            .merge(axes)
            .attr('points', (d) => d)
            .attr('fill', (d, i) => i % 2 === 0 ? config.axisfillColor[0] : config.axisfillColor[1])
            .attr('stroke', config.axisStrokeColor);

        axes.exit()
            .remove();

        // ----渲染对角线-----
        const line = d3.line();

        const outerPoints = getOuterPoints(points[0]);

        const lines = d3.select('.axes')
            .selectAll('.line')
            .data(outerPoints);

        lines.enter()
            .append('path')
            .attr('class', 'line')
            .merge(lines)
            .attr('d', (d) => {
                return line([
                    [0, 0],
                    [d[0], d[1]]
                ]);
            })
            .attr('stroke', config.axisStrokeColor);

        lines.exit()
            .remove();

        //生成背景多边形的顶点             
        function getPolygonPoints(vertexNum, outerRadius, tickNum) {
            const points = [];
            let polygon;

            if (vertexNum < 3) return points;

            const anglePiece = Math.PI * 2 / vertexNum;
            const radiusReduce = outerRadius / tickNum;

            for (let r = outerRadius; r > 0; r -= radiusReduce) {
                polygon = [];

                for (let i = 0; i < vertexNum; i++) {
                    polygon.push(
                        Math.sin(i * anglePiece) * r + ',' + Math.cos(i * anglePiece) * r
                    );
                }

                points.push(polygon.join(' '));
            }

            return points;
        }

        //得到最外层多边形的顶点
        function getOuterPoints(outerPoints) {
            const points = outerPoints.split(' ').map((d) => d.split(','));
            return points;
        }
    }

    /* ----------------------------渲染文本标签------------------------  */
    chart.renderText = function () {

        const texts = d3.select('.axes')
            .selectAll('.label')
            .data(data);

        texts.enter()
            .append('text')
            .attr('class', 'label')
            .merge(texts)
            .attr('x', (d, i) => Math.sin(i * Math.PI * 2 / data.length) * (config.radius + 20))
            .attr('y', (d, i) => Math.cos(i * Math.PI * 2 / data.length) * (config.radius + 20))
            .attr('text-anchor', (d, i) => computeTextAnchor(data, i))
            .attr('dy', 6.5)       //由于text-anchor属性在垂向上对齐文字底部，故需要使其对齐文字中部
            .text((d) => d.subject_1)
            .attr("fill", "black");

        function computeTextAnchor(data, i) {
            if (data.length < 3) return;

            const angle = i * 360 / data.length;

            if (angle === 0 || Math.abs(angle - 180) < 0.01) {
                return 'middle';
            } else if (angle > 180) {
                return 'end'
            } else {
                return 'start'
            }
        }

    }

    /* ----------------------------渲染数据多边形------------------------  */
    chart.renderPolygons = function () {
        const newData = handleData(data);

        const polygons = chart.body().selectAll('.polygons')
            .data(newData);

        polygons.enter()
            .append('g')
            .attr('class', (d) => 'g-' + d.person)
            .attr('transform', 'translate(' + chart.getBodyWidth() / 2 + ',' + chart.getBodyHeight() / 2 + ')')
            .append('polygon')
            .attr('class', 'polygon')
            .merge(polygons)
            .attr('fill', 'none')
            .attr('stroke', (d, i) => chart._colors(i))
            .attr('stroke-width', '2')
            .attr('points', (d, i) => {
                const miniPolygon = [];
                d.forEach(() => {
                    miniPolygon.push("0,0")
                });
                return miniPolygon.join(' ');
            })
            .transition().duration(config.animateDuration)
            .attr('points', generatePolygons);

        polygons.exit()
            .remove();


        //处理数据，转化数据结构，方便渲染
        function handleData(data) {
            const newData = [];
            Object.keys(data[0]).forEach((key) => {
                if (key !== 'subject_1') {
                    const item = [];
                    item.person = key;
                    newData.push(item);
                }
            });
            data.forEach((d) => {
                newData.forEach((item, i) => {
                    item.push([d.subject_1, d['person' + (i + 1)]]);
                });
            });
            return newData;
        }

        //计算多边形的顶点并生成顶点圆圈
        function generatePolygons(d, index) {
            const points = [];
            const anglePiece = Math.PI * 2 / d.length;
            d.forEach((item, i) => {
                const x = Math.sin(i * anglePiece) * chart.scaleRadius(item[1]);
                const y = Math.cos(i * anglePiece) * chart.scaleRadius(item[1]);
                //添加交点圆圈
                d3.select('.g-' + d.person)
                    .append('circle')
                    .attr('class', 'point-' + d.person)
                    .attr('fill', config.pointsColor)
                    .attr('stroke', chart._colors(index))
                    .attr('cx', 0)
                    .attr('cy', 0)
                    .attr('r', config.pointsSize)
                    .transition().duration(config.animateDuration)
                    .attr('cx', x)
                    .attr('cy', y)

                points.push(x + ',' + y);
            });

            return points.join(' ');
        }

    }

    /* ----------------------------渲染图标题------------------------  */
    chart.renderTitle = function () {
        chart.svg().append('text')
            .classed('title', true)
            .attr('x', chart.width() / 2)
            .attr('y', 0)
            .attr('dy', '4em')
            .text(config.title)
            // .attr('fill', config.textColor)
            .attr('fill', "black")
            .attr('text-anchor', 'middle')
            .attr('font-size', 25)
            // .attr('stroke', config.textColor);
            .attr('stroke', "black");
    }
    var t1, t2, t3, t4;
    chart.renderLegend = function () {
        t1 = chart.svg().append("rect")
            .classed('legend', true)
            .attr('x', chart.width() * 3 / 4)
            .attr('y', chart.height() / 4 - 50)
            .attr("width", 15)
            .attr("height", 15)
            .attr("fill", chart._colors(0))
        chart.svg().append('text')
            .classed('title', true)
            .attr('x', chart.width() * 3 / 4 + 40 + 20)
            .attr('y', chart.height() / 4 - 36)
            // .attr('dy', '2em')
            .text("Alldrik")
            // .attr('fill', config.textColor)
            .attr('text-anchor', 'middle')
            .attr("fill", "black");
        // .attr('stroke', config.textColor);

        var dy = 20;
        t2 = chart.svg().append("rect")
            .classed('legend', true)
            .attr('x', chart.width() * 3 / 4)
            .attr('y', chart.height() / 4 - 50 + dy)
            .attr("width", 15)
            .attr("height", 15)
            .attr("fill", chart._colors(1)).remove()
        chart.svg().append('text')
            .classed('title', true)
            .attr('x', chart.width() * 3 / 4 + 40 + 20)
            .attr('y', chart.height() / 4 - 36 + dy)
            // .attr('dy', '2em')
            .text("Stagar")
            // .attr('fill', config.textColor)
            .attr('text-anchor', 'middle')
            .attr("fill", "black").remove();
        // .attr('stroke', config.textColor);

        t3 = chart.svg().append("rect")
            .classed('legend', true)
            .attr('x', chart.width() * 3 / 4)
            .attr('y', chart.height() / 4 - 50 + 2 * dy)
            .attr("width", 15)
            .attr("height", 15)
            .attr("fill", chart._colors(2)).remove()
        chart.svg().append('text')
            .classed('title', true)
            .attr('x', chart.width() * 3 / 4 + 40 + 20)
            .attr('y', chart.height() / 4 - 36 + 2 * dy)
            // .attr('dy', '2em')
            .text("Nelsan")
            // .attr('fill', config.textColor)
            .attr('text-anchor', 'middle')
            .attr("fill", "black").remove();
        // .attr('stroke', config.textColor);

        t4 = chart.svg().append("rect")
            .classed('legend', true)
            .attr('x', chart.width() * 3 / 4)
            .attr('y', chart.height() / 4 - 50 + 3 * dy)
            .attr("width", 15)
            .attr("height", 15)
            .attr("fill", chart._colors(3)).remove()
        chart.svg().append('text')
            .classed('title', true)
            .attr('x', chart.width() * 3 / 4 + 40 + 20)
            .attr('y', chart.height() / 4 - 36 + 3 * dy)
            // .attr('dy', '2em')
            .text("Filnner")
            // .attr('fill', config.textColor)
            .attr('text-anchor', 'middle')
            .attr("fill", "black").remove();
        // .attr('stroke', config.textColor);

    }
    var flag = true, flag2 = true;
    chart.clickLegend = function () {
        t1.on('click', function () {
            //50以下是灰色    50~70绿色  70到80黄色  80~90橙色 90以上红色
            var color = ["gray", "green", "orange", "orangeRed", "red"];
            var data08Cris = [92, 93, 89, 64, 79, 80]
            // var color08Cris=["red","red","orange","gray","yellow","yellow"]
            var color08Cris = [];
            for (var i = 0; i < data08Cris.length; i++) {
                if (data08Cris[i] >= 90) {
                    color08Cris[i] = "red";
                } else if (data08Cris[i] >= 80) {
                    color08Cris[i] = "orangeRed";
                } else if (data08Cris[i] >= 70) {
                    color08Cris[i] = "orange";
                } else if (data08Cris[i] >= 50) {
                    color08Cris[i] = "green";
                } else color08Cris[i] = "gray";
            }
            var X = [], Y = [];
            for (var i = 0; i < data.length; i++) {
                X[i] = Math.sin(i * Math.PI * 2 / data.length) * (config.radius + 20) + chart.getBodyWidth() / 2 + 70;
                Y[i] = Math.cos(i * Math.PI * 2 / data.length) * (config.radius + 20) + chart.getBodyHeight() / 2 + 70;
                // console.log(X[i]); console.log(Y[i]);
            }
            //设置偏移量
            var dx = [0, 40, 40, 0, -40, -40];
            var dy = [20, 0, 0, -20, 0, 0];
            if (flag) {
                for (var i = 0; i < data.length; i++) {
                    chart.svg()
                        .append('rect')
                        .classed('tip1', true)
                        .attr('x', X[i] + dx[i])
                        .attr('y', Y[i] + dy[i])
                        .attr("width", 20)
                        .attr("height", 20)
                        .attr("fill", color08Cris[i])
                        .append("text")
                        .attr("fill", "black")
                        .text(data08Cris[i]);
                    chart.svg()
                        .append('text')
                        .classed('tip1', true)
                        .attr('x', X[i] + dx[i] + 1)
                        .attr('y', Y[i] + dy[i] + 15)
                        .attr("fill", "black")
                        .text(data08Cris[i]);
                }
                flag = false;
            }
            else {
                d3.selectAll('.tip1').remove();
                flag = true;
            }

        })
        t2.on('click', function () {
            //50以下是灰色    50~70绿色  70到80黄色  80~90橙色 90以上红色
            var color = ["gray", "green", "orange", "orangeRed", "red"];
            var data08Stagar = [94, 96, 85, 50, 81, 64]
            // var color08Stagar=["red","red","orange","gray","yellow","yellow"]
            var color08Stagar = [];
            for (var i = 0; i < data08Stagar.length; i++) {
                if (data08Stagar[i] >= 90) {
                    color08Stagar[i] = "red";
                } else if (data08Stagar[i] >= 80) {
                    color08Stagar[i] = "orangeRed";
                } else if (data08Stagar[i] >= 70) {
                    color08Stagar[i] = "orange";
                } else if (data08Stagar[i] >= 50) {
                    color08Stagar[i] = "green";
                } else color08Stagar[i] = "gray";
            }
            var X = [], Y = [];
            for (var i = 0; i < data.length; i++) {
                X[i] = Math.sin(i * Math.PI * 2 / data.length) * (config.radius + 20) + chart.getBodyWidth() / 2 + 70;
                Y[i] = Math.cos(i * Math.PI * 2 / data.length) * (config.radius + 20) + chart.getBodyHeight() / 2 + 70;
                // console.log(X[i]); console.log(Y[i]);
            }
            //设置偏移量
            var dx = [0, 60, 60, 0, -60, -60];
            var dy = [40, 0, 0, -40, 0, 0];
            if (flag2) {
                for (var i = 0; i < data.length; i++) {
                    chart.svg()
                        .append('rect')
                        .classed('tip2', true)
                        .attr('x', X[i] + dx[i])
                        .attr('y', Y[i] + dy[i])
                        .attr("width", 20)
                        .attr("height", 20)
                        .attr("fill", color08Stagar[i])
                        .append("text")
                        .attr("fill", "black")
                        .text(data08Stagar[i]);
                    chart.svg()
                        .append('text')
                        .classed('tip2', true)
                        .attr('x', X[i] + dx[i] + 1)
                        .attr('y', Y[i] + dy[i] + 15)
                        .attr("fill", "black")
                        .text(data08Stagar[i]);
                }
                flag2 = false;
            }
            else {
                d3.selectAll('.tip2').remove();
                flag2 = true;
            }
        })
    }
    /* ----------------------------绑定鼠标交互事件------------------------  */
    chart.addMouseOn = function () {
        d3.selectAll('.polygon')
            .on('mouseover', function (d) {
                const e = d3.event;
                const position = d3.pointer(event, [, chart.svg().node()]);

                d3.select(e.target)
                    .attr('stroke-width', '4');
                if (d.person == "person1") {
                    chart.svg()
                        .append('text')
                        .classed('name', true)
                        .attr('x', position[0] + 5)
                        .attr('y', position[1])
                        .attr('fill', config.textColor)
                        // .text("nihao");
                        .text("Alldrik");
                }
                if (d.person == "person2") {
                    chart.svg()
                        .append('text')
                        .classed('name', true)
                        .attr('x', position[0] + 5)
                        .attr('y', position[1])
                        .attr('fill', config.textColor)
                        // .text("nihao");
                        .text("Stagar");
                }
                if (d.person == "person3") {
                    chart.svg()
                        .append('text')
                        .classed('name', true)
                        .attr('x', position[0] + 5)
                        .attr('y', position[1])
                        .attr('fill', config.textColor)
                        // .text("nihao");
                        .text("Nelsan");
                }
                if (d.person == "person4") {
                    chart.svg()
                        .append('text')
                        .classed('name', true)
                        .attr('x', position[0] + 5)
                        .attr('y', position[1])
                        .attr('fill', config.textColor)
                        // .text("nihao");
                        .text("Filnner");
                }


            })
            .on('mouseleave', function () {
                const e = d3.event;
                d3.select(e.target)
                    .attr('stroke-width', '2');
                d3.selectAll('.name').remove();
                // d3.select('.tip').remove();
            })
    }

    chart.render = function () {
        chart.renderTitle();
        chart.renderAxes();
        chart.renderText();
        chart.renderPolygons();
        chart.addMouseOn();
        chart.renderLegend();
        // chart.clickLegend();
    }
    chart.renderChart();
});














