<template>
    <div>
        <p>HOLA</p>

    </div>
</template>

<script>
    export default {
        name: 'ChartPie',
        props: ['items'],
        data () {
            return {
                tableHeaders: [
                    { text: 'Name',  sortable: true, value: 'name'},
                    { text: 'Value',  sortable: true, value: 'value'},
                ],   
            }
        },
        methods:{           
        },
    }
</script>
<style scoped>
</style>
