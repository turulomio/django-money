Vue.component('table-investmentoperationshistorical-homegeneousinvestment', {
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
        }
    },
    template: `
        <v-data-table dense :headers="tableHeaders" :items="items" class="elevation-1" disable-pagination  hide-default-footer sort-by="['datetime']" fixed-header :height="$attrs.height">
            <template v-slot:[\`item.dt_end\`]="{ item }">
            {{ localtime(item.dt_end)}}
            </template>
            <template v-slot:[\`item.gross_start_investment\`]="{ item }">
            {{ currency_html(item.gross_start_investment, currency_investment)}}
            </template>
            <template v-slot:[\`item.gross_end_investment\`]="{ item }">
            {{ currency_html(item.gross_end_investment, currency_investment)}}
            </template>
            <template v-slot:[\`item.gains_gross_investment\`]="{ item }" >
                <div v-html="currency_html(item.gains_gross_investment, currency_investment)"></div>
            </template>
            <template v-slot:[\`item.commissions_investment\`]="{ item }">
            {{ currency_html(item.commissions_investment, currency_investment)}}
            </template>
            <template v-slot:[\`item.taxes_investment\`]="{ item }">
            {{ currency_html(item.taxes_investment, currency_investment)}}
            </template>
            <template v-slot:[\`item.gains_net_investment\`]="{ item }">
                <div v-html="currency_html(item.gains_net_investment, currency_investment)"></div>
            </template>
        </v-data-table>   
    `,
    data: function(){
        return {
            tableHeaders: [
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
            ],   
        }
    },
    computed:{
    },
    methods: {
        editIO(item){
            window.location.href=`${this.url_root}investmentoperation/update/${item.id}`
        }
    },
    mounted(){
    }
})
