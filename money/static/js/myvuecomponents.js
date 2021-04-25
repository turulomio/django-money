Vue.component('todo-item', {
  template: '<li>This is a todo</li>'
})

Vue.component('chart-pie', {
    props: ['items', 'name', 'height','key'],
    template: `
        <v-card flat :style="styleheight">
            <v-chart autoresize :option="options" :key="key"/>
        </v-card>
    `,
    data: function () {
        return {

        }
    },
    computed:{
        options: function(){
            return {
                tooltip: {
                    trigger: "item",
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                series: [
                    {
                        name: this.name,
                        type: "pie",
                        radius: "80%",
                        center: ["50%", "50%"],
                        data: this.items,
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: "rgba(0, 0, 0, 0.5)"
                            }
                        }
                    }
                ]
            }
        },
        styleheight: function(){
            return `height: ${this.height};`
        }
    }
//     created(){
//         
//     }
})

