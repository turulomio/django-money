Vue.component('my-datetimepicker', {
    props: {
        value: {
            required: true
        },
    },
    template: `
    <div>
        <v-menu v-model="menu" :close-on-content-click="false" :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
            <template v-slot:activator="{ on, attrs }">
                <v-row justify="center" align="center">
                    <v-text-field v-model="localValue" :name="$attrs.name" :label="$attrs.label" prepend-icon="mdi-calendar" readonly v-bind="attrs" v-on="on"></v-text-field>
                    <v-icon x-small @click="localValue=''">mdi-backspace</v-icon>
                </v-row>
            </template>
            <v-date-picker v-model="date" @change="on_change()"></v-date-picker>
            <v-time-picker  format="24hr" v-model="time" use-seconds @change="on_change()"></v-date-picker>

            <v-btn class="ml-4" color="error" @click="menu=false" >{{buttonCloseText}}</v-btn>
        </v-menu>
    </div>
    `,
    data: function(){
        return {
            menu: false,
            date: "",
            time: "",
            localValue: "",
            buttonCloseText: gettext("Close")
        }
    },
    watch: {
        localValue (newValue) {
            console.log("Setting localValue")
            console.log(newValue)
            this.$emit('input', newValue)
        },
        value (newValue) {
            console.log("Setting value")
            console.log(newValue)
            this.localValue = newValue
            if (newValue==""){
                this.date=new Date().toISOString().substring(0,10)
                this.time=new Date().toISOString().substring(11,19)
            } else {
                var arr=this.datetimestring2valuestrings(newValue)
                this.date=arr[0]
                this.time=arr[1]
            }
        }
    },
    methods: {
        on_change(){
            this.localValue=this.valuestrings2datetimestring(this.date,this.time)
            
        },
        datetimestring2valuestrings(s){
            return new Array(
                s.substring(0,10),
                s.substring(11,19)
            )
        },
        valuestrings2datetimestring(date_str, time_str){
            if (date_str=="" || time_str==""){
                return moment().format().replace("T", " ")
            }
            var joinDate=new Date(date_str.substring(0,4),date_str.substring(5,7)-1,date_str.substring(8,10),time_str.substring(0,2),time_str.substring(3,5),time_str.substring(6,8))
            return moment(joinDate).format().replace("T", " ")
            
        },
        setWithJsDate(jsdate){
            console.log(jsdate)
            console.log(jsdate.toISOString())
            this.localValue=moment(jsdate).format().replace("T", " ")
        },
        setWithStrings(date_str, time_str){
            this.localValue=this.valuestrings2datetimestring(date_str, time_str)
        }
        
        
    },
    mounted(){
        console.log("MONTANDO")
        if (this.value==""){
            this.localValue=this.valuestrings2datetimestring("","")
        }
        
    }
})
