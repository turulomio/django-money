Vue.component('table-investmentoperationshistorical', {
    props: {
        items: {
            required: true
        },
        currency_account: {
            required: true,
            default:"EUR"
        },
        currency_investment: {
            required: true,
            default:"EUR"
        },
        currency_user:{
            required: true,
            default:"EUR"
        },
        url_root:{
            required:true
        },
        homogeneous:{
            required:true,
            default:true
        },
        output:{
            required:true,
            default:"account",
        },
    },
    template: `
        <v-data-table dense :headers="table_headers()" :items="items" class="elevation-1" disable-pagination  hide-default-footer sort-by="['datetime']" fixed-header :height="$attrs.height">
            <template v-slot:[\`item.dt_end\`]="{ item }">
            {{ localtime(item.dt_end)}}
            </template>
            <template v-slot:[\`item.gross_start_user\`]="{ item }">
                <div v-html="currency(item.gross_start_user)"></div>
            </template>
            <template v-slot:[\`item.gross_end_user\`]="{ item }">
                <div v-html="currency(item.gross_end_user)"></div>
            </template>
            <template v-slot:[\`item.gains_gross_user\`]="{ item }">
                <div v-html="currency(item.gains_gross_user)"></div>
            </template>
            <template v-slot:[\`item.commissions_user\`]="{ item }">
                <div v-html="currency(item.commissions_user)"></div>
            </template>
            <template v-slot:[\`item.taxes_user\`]="{ item }">
                <div v-html="currency(item.taxes_user)"></div>
            </template>
            <template v-slot:[\`item.gains_net_user\`]="{ item }">
                <div v-html="currency(item.gains_net_user)"></div>
            </template>
            
            
            <template v-slot:[\`item.gross_start_account\`]="{ item }">
                <div v-html="currency(item.gross_start_account)"></div>
            </template>
            <template v-slot:[\`item.gross_end_account\`]="{ item }">
                <div v-html="currency(item.gross_end_account)"></div>
            </template>
            <template v-slot:[\`item.gains_gross_account\`]="{ item }">
                <div v-html="currency(item.gains_gross_account)"></div>
            </template>
            <template v-slot:[\`item.commissions_account\`]="{ item }">
                <div v-html="currency(item.commissions_account)"></div>
            </template>
            <template v-slot:[\`item.taxes_account\`]="{ item }">
                <div v-html="currency(item.taxes_account)"></div>
            </template>
            <template v-slot:[\`item.gains_net_account\`]="{ item }">
                <div v-html="currency(item.gains_net_account)"></div>
            </template>
            
            
            <template v-slot:[\`item.gross_start_investment\`]="{ item }">
                <div v-html="currency(item.gross_start_investment)"></div>
            </template>
            <template v-slot:[\`item.gross_end_investment\`]="{ item }">
                <div v-html="currency(item.gross_end_investment)"></div>
            </template>
            <template v-slot:[\`item.gains_gross_investment\`]="{ item }" >
                <div v-html="currency(item.gains_gross_investment)"></div>
            </template>
            <template v-slot:[\`item.commissions_investment\`]="{ item }">
                <div v-html="currency(item.commissions_investment)"></div>
            </template>
            <template v-slot:[\`item.taxes_investment\`]="{ item }">
                <div v-html="currency(item.taxes_investment)"></div>
            </template>
            <template v-slot:[\`item.gains_net_investment\`]="{ item }">
                <div v-html="currency(item.gains_net_investment)"></div>
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
        currency(value){
            if (this.output=="account"){
                return currency_html(value, this.currency_account)
            } else if (this.output=="investment"){
                return currency_html(value, this.currency_investment)
            } else if (this.output=="user"){
                return currency_html(value, this.currency_user)
            }
        },
        table_headers(){
            if (this.output=="account"){
                return [
                    { text: gettext('Date and time'), value: 'dt_end',sortable: true },
                    { text: gettext('Years'), value: 'years',sortable: true },
                    { text: gettext('Operation'), value: 'operationstypes',sortable: true },
                    { text: gettext('Shares'), value: 'shares',sortable: false, align:"right"},
                    { text: gettext('Gross start'), value: 'gross_start_account',sortable: false, align:"right"},
                    { text: gettext('Gross end'), value: 'gross_end_account',sortable: false, align:"right"},
                    { text: gettext('Gains gross'), value: 'gains_gross_account',sortable: false, align:"right"},
                    { text: gettext('Commission'), value: 'commissions_account',sortable: false, align:"right"},
                    { text: gettext('Taxes'), value: 'taxes_account',sortable: false, align:"right"},
                    { text: gettext('Gains'), value: 'gains_net_account',sortable: false, align:"right"},
                ]
            } else if (this.output=="investment"){
                return [
                    { text: gettext('Date and time'), value: 'dt_end',sortable: true },
                    { text: gettext('Years'), value: 'years',sortable: true },
                    { text: gettext('Operation'), value: 'operationstypes',sortable: true },
                    { text: gettext('Shares'), value: 'shares',sortable: false, align:"right"},
                    { text: gettext('Gross start'), value: 'gross_start_investment',sortable: false, align:"right"},
                    { text: gettext('Gross end'), value: 'gross_end_investment',sortable: false, align:"right"},
                    { text: gettext('Gains gross'), value: 'gains_gross_investment',sortable: false, align:"right"},
                    { text: gettext('Commission'), value: 'commissions_investment',sortable: false, align:"right"},
                    { text: gettext('Taxes'), value: 'taxes_investment',sortable: false, align:"right"},
                    { text: gettext('Gains'), value: 'gains_net_investment',sortable: false, align:"right"},
                ]
            } else if (this.output=="user"){
                return [
                    { text: gettext('Date and time'), value: 'dt_end',sortable: true },
                    { text: gettext('Years'), value: 'years',sortable: true },
                    { text: gettext('Operation'), value: 'operationstypes',sortable: true },
                    { text: gettext('Shares'), value: 'shares',sortable: false, align:"right"},
                    { text: gettext('Gross start'), value: 'gross_start_user',sortable: false, align:"right"},
                    { text: gettext('Gross end'), value: 'gross_end_user',sortable: false, align:"right"},
                    { text: gettext('Gains gross'), value: 'gains_gross_user',sortable: false, align:"right"},
                    { text: gettext('Commission'), value: 'commissions_user',sortable: false, align:"right"},
                    { text: gettext('Taxes'), value: 'taxes_user',sortable: false, align:"right"},
                    { text: gettext('Gains'), value: 'gains_net_user',sortable: false, align:"right"},
                ] 
            }
        },
    },
})