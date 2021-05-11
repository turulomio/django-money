Vue.component('table-investmentoperations-homegeneous', {
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
            <template v-slot:[\`item.datetime\`]="{ item }">
            {{ localtime(item.datetime)}}
            </template>
            <template v-slot:[\`item.price\`]="{ item }">
            {{ currency_string(item.price, currency_investment)}}
            </template>
            <template v-slot:[\`item.gross_investment\`]="{ item }">
            {{ currency_string(item.price, currency_investment)}}
            </template>
            <template v-slot:[\`item.commission\`]="{ item }">
            {{ currency_string(item.price, currency_investment)}}
            </template>
            <template v-slot:[\`item.taxes\`]="{ item }">
            {{ currency_string(item.price, currency_investment)}}
            </template>
            <template v-slot:[\`item.net_investment\`]="{ item }">
            {{ currency_string(item.price, currency_investment)}}
            </template>
            <template v-slot:[\`item.actions\`]="{ item }">
                <v-icon small class="mr-2" @click="editIO(item)">mdi-pencil</v-icon>
            </template>
        </v-data-table>   
    `,
    data: function(){
        return {
            tableHeaders: [
                { text: gettext('Date and time'), value: 'datetime',sortable: true },
                { text: gettext('Operation'), value: 'operationstypes',sortable: true },
                { text: gettext('Shares'), value: 'shares',sortable: false, align:"right"},
                { text: gettext('Price'), value: 'price',sortable: false, align:"right"},
                { text: gettext('Gross'), value: 'gross_investment',sortable: false, align:"right"},
                { text: gettext('Commission'), value: 'commission',sortable: false, align:"right"},
                { text: gettext('Taxes'), value: 'taxes',sortable: false, align:"right"},
                { text: gettext('Net'), value: 'net_investment',sortable: false, align:"right"},
                { text: gettext('Currency factor'), value: 'currency_conversion',sortable: false, align:"right"},
                { text: gettext('Comment'), value: 'comment',sortable: false},
                { text: gettext('Actions'), value: 'actions', sortable: false },
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
        if (this.currency_investment==this.currency_account){
            return this.tableHeaders.splice(8,1)
        } else {
            return this.tableHeaders
        }
    }
})
