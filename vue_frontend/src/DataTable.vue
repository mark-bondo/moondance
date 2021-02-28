<template>
    <v-app>
        <highcharts class="chart" :options="chartOptions"></highcharts>

        <v-card class="ma-5">
            <v-card-title>API Report Demo</v-card-title>
            <v-card-text>
                <v-row>
                    <v-col cols="4">
                        <v-combobox
                            v-model="api"
                            :items="apiList"
                            label="Select an API"
                            class="mx-5"
                        ></v-combobox>
                    </v-col>
                </v-row>
                <v-row>
                    <v-col cols="12">
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-app>
</template>

<script>
export default {
    name: 'dataTable',
    props: [],
    data: function() {
        return {
            apiList: ["One", "Two", "Three"],
            api: {
                text: null,
                value: null
            },
            chartOptions: {
                title: {
                    text: 'Solar Employment Growth by Sector, 2010-2016'
                },

                subtitle: {
                    text: 'Source: thesolarfoundation.com'
                },

                yAxis: {
                    title: {
                        text: 'Number of Employees'
                    }
                },

                xAxis: {
                    accessibility: {
                        rangeDescription: 'Range: 2010 to 2017'
                    }
                },

                legend: {
                    layout: 'vertical',
                    align: 'right',
                    verticalAlign: 'middle'
                },

                plotOptions: {
                    series: {
                        label: {
                            connectorAllowed: false
                        },
                        pointStart: 2010
                    }
                },

                series: [{
                    name: 'Installation',
                    data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
                }, {
                    name: 'Manufacturing',
                    data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
                }, {
                    name: 'Sales & Distribution',
                    data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
                }, {
                    name: 'Project Development',
                    data: [null, null, 7988, 12169, 15112, 22452, 34400, 34227]
                }, {
                    name: 'Other',
                    data: [12908, 5948, 8105, 11248, 8989, 11816, 18274, 18111]
                }]
            }
        };
    },
    // components: {
    //     HighchartsVue
    // },
    computed: {
    },
    watch: {
    },
    mounted(){
        this.$http.post(`/reports/get-top-sellers`,{
            // data: params
        }).then(response => {
            this.series = response.data.series;
        })
    },
    methods: {
        parseDates(){

        }
        // onGridReady() {
        //     var vm = this;
        //     var api_id = this.api.value;
        //     if(api_id){
        //         const datasource = {
        //             getRows(params) {
        //                 vm.$http.post(`/api/2021-01/${api_id}/get/`, {
        //                     data: params.request,
        //                     headers: { 'Content-Type': 'application/json; charset=utf-8' }
        //                 }).then(response => {
        //                     var lastRow = response.data.rowData.length;
        //                     params.successCallback(response.data.rowData, vm.rowCount)
        //                     vm.columnDefs = response.data.columnDefs;
        //                     vm.getRowCount(lastRow);
        //                 })
        //             }
        //         };
        //         this.gridOptions.api.setServerSideDatasource(datasource);
        //     }
        // },
    }
};
</script>