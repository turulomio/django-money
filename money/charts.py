
def list_dt_to_jsarray(l):
    r="["
    for dt in l:
        r=r+f"new Date({dt.year}, {dt.month}, {dt.day}, {dt.hour}, {dt.minute}, {dt.second},  0),"
    r=r[:-1]+"]"
    print(r)
    return r






def chart_lines_total(list_dt, list_values):
#    js_dt=list_dt_to_jsarray(list_dt)
    return f"""
    <div style="width:75%;">
        <canvas id="canvas"></canvas>
</div>
	<script>
    var datab=[{{x:new Date(2020, 2, 15, 18, 37, 39), y:12}}, {{x:new Date(2020, 2, 16, 18, 37, 39), y:14}}, ];
		var timeFormat = 'YYYY-MM-DD HH:mm:SS';
		var config = {{
			type: 'line',
			data: {{
				labels: [],
				datasets: [{{
                    label: "HOLA", 
					data: datab,
					backgroundColor:'rgb(255,0,0)',
					borderColor: 'rgb(255,0,0)',
					fill: false,
				}}, ]
			}},
			options: {{
				title: {{
					text: 'Chart.js Line Chart'
				}},
				scales: {{
					xAxes: [{{
						type: 'time',
						time: {{
							parser: timeFormat,
						}},
						scaleLabel: {{
							display: true,
							labelString: 'Date'
						}}
					}}],
					yAxes: [{{
						scaleLabel: {{
							display: true,
							labelString: 'Value'
						}}
					}}]
				}}
			}}
		}};




		window.onload = function() {{
			var ctx = document.getElementById('canvas').getContext('2d');
			window.myLine = new Chart(ctx, config);

		}};


	</script>"""
