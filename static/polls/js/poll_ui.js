socket = new WebSocket("ws://" + window.location.host);

var width = 420,
    barHeight = 50;

var x = d3.scale.linear()
    .domain([0, vote_limit])
    .range([12, width]);

var chart = d3.select(".chart")
	.attr("viewBox", "0 0 " + width + " " + ((barHeight + 25 + 5) * data.length - 5));

var bar = chart.selectAll("g")
    .data(data)
  .enter().append("g")
  	.attr("id", function(d) { return d.id; })
	.attr("transform", function(d, i) {
		if(i > 0) { return "translate(0," + ((i * barHeight) + ((i+1) * 25) + (i * 5)) + ")"; }
		else { return "translate(0," + 25 + ")"; }
	})
	.on("click", function(d) {
		if(has_voted == false || one_vote_only == false){
			socket.send(JSON.stringify({
				"question_id": question_id,
				"choice_id": d3.select(this).attr("id")
			}));
			if(one_vote_only == true) {
				d3.select(".panel-body").text("your choice has been tallied.\nThanks for your contribution.");
				has_voted = true;
			}
		}
	});

bar.append("rect")
	.attr("width", width)
	.attr("height", barHeight - 1)
	.attr("fill", "lightskyblue");

bar.append("rect")
    .attr("class", "votes_bar")
    .attr("width", function(d) { return x(d.votes); })
    .attr("height", barHeight - 1)
    .attr("fill", "steelblue");

bar.append("text")
	.attr("class", "votes_text")
    .attr("x", function(d) { return x(d.votes) - 3; })
    .attr("y", barHeight / 2)
    .attr("dy", ".35em")
    .text(function(d) { return d.votes; });

var labels = chart.append("g")
  .selectAll("text")
	.data(data)
  .enter().append("text")
  	.attr("class", "label_text")
  	.attr("transform", function(d, i) {
  		if(i > 0) { return "translate(2," + ((i * barHeight) + ((i+1) * 25) + (i * 5)  - 6) + ")"; }
  		else { return "translate(2," + 19 + ")"; }
  	})
    .text(function(d) { return d.choice_text; });

socket.onmessage = function(message) {
	data = JSON.parse(message.data);
	var x = d3.scale.linear()
    	.domain([0, vote_limit])
    	.range([12, width]);
	bar.data(data)
	bar.select(".votes_bar")
		.attr("width", function(d) { return x(d.votes); });
	bar.select("text")
		.attr("x", function(d) { return x(d.votes) - 3; })
		.text(function(d) { return d.votes; });
}
