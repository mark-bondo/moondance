<template>
    <v-app>
        <v-card class="ma-5">
            <v-card-title>Sales Dashboard</v-card-title>
            <v-card-text>
                <v-row>
                    <v-col cols="4">
                        <v-combobox
                            v-model="api"
                            :items="apiList"
                            label="Select a Product"
                            class="mx-5"
                        ></v-combobox>
                    </v-col>
                </v-row>
                <v-row>
                    <v-col cols="12">
                    </v-col>
                </v-row>
                <v-row>
                  <v-col cols="6">
                    <highcharts 
                      class="chart" 
                      :options="chartOptions"
                    >
                    </highcharts>
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
                type: "column",
                title: {
                    text: 'Top Bar Soaps'
                },

                credits: {
                    text: ''
                },

                yAxis: {
                    title: {
                        text: 'Quantity Sold'
                    }
                },

                xAxis: {
                    type: "datetime",
                    // accessibility: {
                    //     rangeDescription: 'Range: 2010 to 2017'
                    // }
                },

                legend: {
                    // layout: 'vertical',
                    align: 'center',
                    verticalAlign: 'bottom'
                },

                plotOptions: {
                    series: {
                        label: {
                            connectorAllowed: false
                        },
                        // pointStart: 2010
                    },
                    column: {
                        stacking: 'normal',
                        dataLabels: {
                            enabled: true
                        }
                    },
                },

                series: []
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
        this.$http.get(`/reports/top-sellers/`,{
            // data: params
        }).then(response => {
            this.chartOptions.series = this.parseDates(response.data.series);
             console.log(this.chartOptions.series)
        })
    },
    methods: {
        parseDates(series){
            for (let i = 0; i < series.length; i++) {
                var obj = series[i];
                
                for (let x = 0; x < obj.data.length; x++) {
                    obj.data[x][0] = Date.parse(obj.data[x][0]);
                }
            }

            return series;
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