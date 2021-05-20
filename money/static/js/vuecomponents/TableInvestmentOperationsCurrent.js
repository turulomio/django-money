Vue.component('table-investmentoperationscurrent', {
    props: {
        items: {
            required: true
        },
        currency_account: {
            required: true
        },
        currency_investment: {
            required: true
        },
        url_root:{
            required:true
        },
        homogeneous:{
            required:true,
            default:true,
        },
        output:{
            required:true,
            default:"account",
        },
    },
    template: `
        <v-data-table dense :headers="table_headers()" :items="items" class="elevation-1" disable-pagination  hide-default-footer sort-by="['datetime']" fixed-header :height="$attrs.height">
            <template v-slot:[\`item.datetime\`]="{ item }">
            {{ localtime(item.datetime)}}
            </template>          
            <template v-slot:[\`item.gains_gross_account\`]="{ item }">
                <div v-html="currency(item.gains_gross_account)"></div>
            </template>        
            <template v-slot:[\`item.gains_gross_investment\`]="{ item }">
                <div v-html="currency(item.gains_gross_investment)"></div>
            </template>  
            
            <template v-slot:[\`item.price_account\`]="{ item }">
                <div v-html="currency(item.price_account)"></div>
            </template>  
            <template v-slot:[\`item.price_investment\`]="{ item }">
                <div v-html="currency(item.price_investment)"></div>
            </template>  
            
            <template v-slot:[\`item.invested_account\`]="{ item }">
                <div v-html="currency(item.invested_account)"></div>
            </template>  
            <template v-slot:[\`item.invested_investment\`]="{ item }">
                <div v-html="currency(item.invested_investment)"></div>
            </template> 
            
            <template v-slot:[\`item.balance_account\`]="{ item }">
                <div v-html="currency(item.balance_account)"></div>
            </template>  
            <template v-slot:[\`item.balance_investment\`]="{ item }">
                <div v-html="currency(item.balance_investment)"></div>
            </template>  
            
            <template v-slot:[\`item.percentage_annual_investment\`]="{ item }">
                <div v-html="percentage_html(item.percentage_annual_investment)"></div>
            </template>
            <template v-slot:[\`item.percentage_apr_investment\`]="{ item }">
                <div v-html="percentage_html(item.percentage_apr_investment)"></div>
            </template>
            <template v-slot:[\`item.percentage_total_investment\`]="{ item }">
                <div v-html="percentage_html(item.percentage_total_investment)"></div>
            </template>
        </v-data-table>   
    `,
    data: function(){
        return {
        }
    },
    computed:{
    },
    methods: {
        editIO(item){
            window.location.href=`${this.url_root}investmentoperation/update/${item.id}`
        },
        currency(value){
            if (this.output=="account"){
                return currency_html(value, this.currency_account)
            } else if (this.output=="investment"){
                return currency_html(value, this.currency_investment)
            }percentage_annual_investment
        },
        table_headers(){
            if (this.output=="account"){
                return [
                    { text: gettext('Date and time'), value: 'datetime',sortable: true },
                    { text: gettext('Operation'), value: 'operationstypes',sortable: true },
                    { text: gettext('Shares'), value: 'shares',sortable: false, align:"right"},
                    { text: gettext('Price'), value: 'price_account',sortable: false, align:"right"},
                    { text: gettext('Invested'), value: 'invested_account',sortable: false, align:"right"},
                    { text: gettext('Balance'), value: 'balance_account',sortable: false, align:"right"},
                    { text: gettext('Gross gains'), value: 'gains_gross_account',sortable: false, align:"right"},
                    { text: gettext('% annual'), value: 'percentage_annual_investment',sortable: false, align:"right"},
                    { text: gettext('% APR'), value: 'percentage_apr_investment',sortable: false, align:"right"},
                    { text: gettext('% Total'), value: 'percentage_total_investment',sortable: false, align:"right"},
                ]
            } else if (this.output=="investment"){
                return [
                    { text: gettext('Date and time'), value: 'datetime',sortable: true },
                    { text: gettext('Operation'), value: 'operationstypes',sortable: true },
                    { text: gettext('Shares'), value: 'shares',sortable: false, align:"right"},
                    { text: gettext('Price'), value: 'price_investment',sortable: false, align:"right"},
                    { text: gettext('Invested'), value: 'invested_investment',sortable: false, align:"right"},
                    { text: gettext('Balance'), value: 'balance_investment',sortable: false, align:"right"},
                    { text: gettext('Gross gains'), value: 'gains_gross_investment',sortable: false, align:"right"},
                    { text: gettext('% annual'), value: 'percentage_annual_investment',sortable: false, align:"right"},
                    { text: gettext('% TAE'), value: 'percentage_apr_investment',sortable: false, align:"right"},
                    { text: gettext('% Total'), value: 'percentage_total_investment',sortable: false, align:"right"},
                ]
                
            }
        },
    },
})
