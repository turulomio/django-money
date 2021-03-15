from django.utils.translation import ugettext_lazy as _
from money.reusing.listdict_functions import listdict2list
def list_dt_to_jsarray(l):
    r="["
    for dt in l:
        r=r+f"new Date({dt.year}, {dt.month}, {dt.day}, {dt.hour}, {dt.minute}, {dt.second},  0),"
    r=r[:-1]+"]"
    print(r)
    return r
    
def dt_to_js(dt):
    return f"new Date({dt.year}, {dt.month}, {dt.day}, {dt.hour}, {dt.minute}, {dt.second},  0)"

def data_to_js(list_dt, list_values):
    r="["
    for i in range(list_dt):
        d="{"
        d=d+f" x: {dt_to_js(list_dt[i])},"
        d=d+f" y: {list_values[i]},"
        d=d+"}", 
    r=r[:-1]+"]"
    return r


def listdict_to_chartdata(listdict, key_x,  key_y):
    r="["
    for row in listdict:
        r=r+"{"
        r=r+f" x: {dt_to_js(row[key_x])},"
        r=r+f" y: {row[key_y]},"
        r=r+"},"
    r=r[:-1]+"]"
    return r
    
def listdict_with_ohcl_to_chartdata(listdict, key_date="date", key_open="open",  key_close="close", key_low="low",  key_high="high"):
    r="["
    for row in listdict:
        r=r+"{"
        r=r+f" t: new Date({row[key_date].year}, {row[key_date].month}, {row[key_date].day}, 0, 0, 0), "
        r=r+f" o: {row[key_open]},"
        r=r+f" h: {row[key_high]},"
        r=r+f" c: {row[key_close]},"
        r=r+f" l: {row[key_low]},"
        r=r+"},"
    r=r[:-1]+"]"
    return r


## CHART.JS
def chart_lines_total(listdict, local_currency):
    return f"""
<div style="width:75%;">
    <canvas id="canvas"></canvas>
</div>
<script>
    var timeFormat = 'YYYY-MM-DD HH:mm:SS';
    var config = {{
        type: 'line',
        data: {{
            labels: [],
            datasets: [
                {{
                    label: "{_("Total assets")}", 
                    data: {listdict_to_chartdata(listdict, "datetime", "total_user")},
                    backgroundColor:'rgb(255,0,0)',
                    borderColor: 'rgb(200,0,0)',
                    fill: false,
                }},
                {{
                    label: "{_("Invested assets")}", 
                    data: {listdict_to_chartdata(listdict, "datetime", "invested_user")},
                    backgroundColor:'rgb(0,255,0)',
                    borderColor: 'rgb(0,200,0)',
                    fill: false,
                }}, 
                {{
                    label: "{_("Investments assets")}", 
                    data: {listdict_to_chartdata(listdict, "datetime", "investments_user")},
                    backgroundColor:'rgb(0,0,255)',
                    borderColor: 'rgb(0,0,200)',
                    fill: false,
                }}, 
                {{
                    label: "{_("Accounts assets")}", 
                    data: {listdict_to_chartdata(listdict, "datetime", "accounts_user")},
                    backgroundColor:'rgb(0,255,255)',
                    borderColor: 'rgb(0,200,200)',
                    fill: false,
                }}, 
            ]
        }},
        options: {{
            title: {{
                display: true, 
                text: '{_("Total assets chart")}'
            }},
                scales: {{
                    xAxes: [{{
                        type: 'time',
                        distribution: 'series',
                        time: {{
                            unit: 'month', 
                            parser: timeFormat,
                        }},
                        scaleLabel: {{
                            display: true,
                        }}, 
                    }}],
                    yAxes: [{{
                        scaleLabel: {{
                            display: true,
                            labelString: '{local_currency}'
                        }}, 
                        ticks: {{
                            min: 0
                        }}, 
                    }}]
                }}
            }}
        }};

                        var ctx = document.getElementById('canvas').getContext('2d');
                        window.myLine = new Chart(ctx, config);
        </script>"""
## CHART.JS
def chart_product_quotes_historical(listdict, product):
    ## OJO CHART.JS DEBE ESTAR EN MISMA VERSION QUE FINANCIAL
    return f"""
<div style="width:75%;">
    <canvas id="canvas"></canvas>
</div>
<script>

var ctx = document.getElementById('canvas').getContext('2d');
var chart = new Chart(ctx, {{
        type: 'ohlc',
        data: {{
            datasets: [{{
                label: 'CHRT - Chart.js Corporation',
                data: {listdict_with_ohcl_to_chartdata(listdict)},

            }}]
        }}
}});
</script>"""

## ECHARTS
def chart_product_ranges(prm, name="chart_product_ranges"):            
    ld_ohcl=prm.product.ohclDailyBeforeSplits()    
    
    #Series for variable smas
    sma_series=""
    sma_series_legend=""
    for sma in prm.recomendationMethod2ListSMA():                
        sma_series=sma_series+f"""{{
                    name: 'SMA{sma}',
                    type: 'line',
                    data: calculateMA({sma}, data),
                    smooth: true,
                    showSymbol: false,
                    lineStyle: {{
                        width: 1
                    }}
                }},
"""   
        sma_series_legend=sma_series_legend+f"'SMA{sma}', "
    sma_series_legend=sma_series_legend[:-2]
    
    #Series for product ranges
    ranges_series=""
    for range in prm:
        print(range.recomendation_invest)
        if range.recomendation_invest is True:
            ranges_series=ranges_series+f"""
                 {{
                     type: 'line',
                     data: {str([range.value]*len(ld_ohcl))},
                     tooltip: {{
                       show: false
                     }}
                 }},
"""
    print (ranges_series, "RANGES")

    
    
    
    #Chart
    return f"""
    <div id="{name}" style="width: 80%;height:400px;"></div>
    <script type="text/javascript">
        function calculateMA(dayCount, data) {{
            var result = [];
            for (var i = 0, len = data.length; i < len; i++) {{
                if (i < dayCount) {{
                    result.push('-');
                    continue;
                }}
                var sum = 0;
                for (var j = 0; j < dayCount; j++) {{
                    sum += data[i - j];
                }}
                result.push(sum / dayCount);
            }}
            return result;
        }}
        
        // based on prepared DOM, initialize echarts instance
        var dates={str(listdict2list(ld_ohcl, "date", cast="str"))};
        var data={str(listdict2list(ld_ohcl, "close", cast="float"))};
        var myChart = echarts.init(document.getElementById('{name}'));

        // specify chart configuration item and data
        var option = {{
            legend: {{
                data: ['{prm.product.name}', {sma_series_legend}],
                inactiveColor: '#777',
            }},
            tooltip: {{
                trigger: 'axis',
                axisPointer: {{
                    animation: false,
                    type: 'cross',
                    lineStyle: {{
                        color: '#376df4',
                        width: 2,
                        opacity: 1
                    }}
                }}
            }},
            xAxis: {{
                type: 'category',
                data: dates,
                axisLine: {{ lineStyle: {{ color: '#8392A5' }} }}
            }},
            yAxis: {{
                scale: true,
                axisLine: {{ lineStyle: {{ color: '#8392A5' }} }},
                splitLine: {{ show: false }}
            }},
            grid: {{
                bottom: 80, 
                left:80
            }},
            dataZoom: [{{
                textStyle: {{
                    color: '#8392A5'
                }},
                handleIcon: 'path://M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
                dataBackground: {{
                    areaStyle: {{
                        color: '#8392A5'
                    }},
                    lineStyle: {{
                        opacity: 0.8,
                        color: '#8392A5'
                    }}
                }},
                brushSelect: true
            }}, {{
                type: 'inside'
            }}],
            series: [
                {{
                    type: 'line',
                    name: '{prm.product.name}',
                    data: data,
                }},
                {ranges_series}, 
                {sma_series}, 
            ]
        }};
        // use configuration item and data specified to show chart
        myChart.setOption(option);
    </script>"""
