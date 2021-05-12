Vue.component('table-investmentoperationshistorical-homegeneoususer', {
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
            <template v-slot:[\`item.gross_start_user\`]="{ item }">
                {{ currency_html(item.gross_start_user, currency_investment)}}
            </template>
            <template v-slot:[\`item.gross_end_user\`]="{ item }">
                {{ currency_html(item.gross_end_user, currency_investment)}}
            </template>
            <template v-slot:[\`item.gains_gross_user\`]="{ item }">
                <div v-html="currency_html(item.gains_gross_user, currency_investment)"></div>
            </template>
            <template v-slot:[\`item.commissions_user\`]="{ item }">
                <div v-html="currency_html(item.commissions_user, currency_investment)"></div>
            </template>
            <template v-slot:[\`item.taxes_user\`]="{ item }">
                <div v-html="currency_html(item.taxes_user, currency_investment)"></div>
            </template>
            <template v-slot:[\`item.gains_net_user\`]="{ item }">
                <div v-html="currency_html(item.gains_net_user, currency_investment)"></div>
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
                { text: gettext('Gross start'), value: 'gross_start_user',sortable: false, align:"right"},
                { text: gettext('Gross end'), value: 'gross_end_user',sortable: false, align:"right"},
                { text: gettext('Gains gross'), value: 'gains_gross_user',sortable: false, align:"right"},
                { text: gettext('Commission'), value: 'commissions_user',sortable: false, align:"right"},
                { text: gettext('Taxes'), value: 'taxes_user',sortable: false, align:"right"},
                { text: gettext('Gains'), value: 'gains_net_user',sortable: false, align:"right"},
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
