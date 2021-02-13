<template>
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
                    <div id="contentSection">
                        <ag-grid-vue
                        style="width: 100%; height: 350px;"
                        class="ag-theme-alpine"
                        :gridOptions="gridOptions"
                        :columnDefs="columnDefs"
                        :defaultColDef="defaultColDef"
                        :rowData="rowData"
                        :cacheBlockSize="cacheBlockSize"
                        :rowModelType="rowModelType"
                        :serverSideStoreType="serverSideStoreType"
                        :modules="modules"
                        @grid-ready="onGridReady"
                        ></ag-grid-vue>
                    </div>
                      <div
                        class="text-center mt-3 display"
                      >
                        <v-pagination
                            v-model="page.selected"
                            :length="page.count"
                            :total-visible="7"
                            prev-icon="mdi-menu-left"
                            next-icon="mdi-menu-right"
                        ></v-pagination>
                        <div>
                            records found: {{ rowCount }}
                        </div>

                    </div>
                </v-col>
            </v-row>
        </v-card-text>
    </v-card>
</template>

<script>
import { AgGridVue } from "ag-grid-vue";
import 'ag-grid-enterprise';
import { ServerSideRowModelModule } from '@ag-grid-enterprise/server-side-row-model';
export default {
    name: 'dataTable',
    components: {
        AgGridVue
    },
    props: [],
    data: function() {
        return {
            rowCount: null,
            page: {
                selected: 1,
                url: null,
                count: 0
            },
            apiList: [],
            api: {
                text: null,
                value: null
            },
            modules: [
                ServerSideRowModelModule
            ],
            rowModelType: 'serverSide',
            serverSideStoreType: 'partial',
            cacheBlockSize: 50,
            columnDefs: null,
            rowData: null,
            gridOptions: {
                pagination: true,
                paginationPageSize: 50,
                suppressPaginationPanel: true,
                // debug: true,
            },
            defaultColDef: {
                flex: 1,
                minWidth: 110,
                sortable: true,
                resizable: true,
                floatingFilter: true,
                menuTabs: ['filterMenuTab','generalMenuTab'],
            },
        };
    },
    computed: {
    },
    watch: {
        api(){
            this.rowCount = null;
            this.onGridReady();
        },
        "page.selected"(value){
            console.log(value)
            this.gridApi.paginationGoToPage(value-1);
        },
        rowCount(value){
            this.page.count = Math.ceil(value / this.gridOptions.paginationPageSize);
        }
    },
    mounted(){
        this.gridApi = this.gridOptions.api;
        this.gridColumnApi = this.gridOptions.columnApi;
        this.getApiList();
    },
    methods: {
        onGridReady() {
            var vm = this;
            var api_id = this.api.value;
            if(api_id){
                const datasource = {
                    getRows(params) {
                        vm.$http.post(`/api/2021-01/${api_id}/get/`, {
                            data: params.request,
                            headers: { 'Content-Type': 'application/json; charset=utf-8' }
                        }).then(response => {
                            var lastRow = response.data.rowData.length;
                            params.successCallback(response.data.rowData, vm.rowCount)
                            vm.columnDefs = response.data.columnDefs;
                            vm.getRowCount(lastRow);
                        })
                    }
                };
                this.gridOptions.api.setServerSideDatasource(datasource);
            }
        },
        getRowCount(rowCount) {
            let currentUrl = this.api.value + JSON.stringify(this.gridApi.getFilterModel());
            if(currentUrl !== this.page.url){
                if(rowCount < 50){
                    this.rowCount = rowCount;
                }
                else{
                    this.rowCount = null;
                    let params = {
                        filterModel: this.gridApi.getFilterModel(),
                        rowCountOnly: true
                    }
                    this.$http.post(`/api/2021-01/${this.api.value}/get/`,{
                        data: params
                    }).then(response => {
                        this.page.url = this.api.value + JSON.stringify(params.filterModel);
                        this.rowCount = response.data.rowCount;
                    })
                }
            }
        },
        getApiList (){
            this.$http.get('/api/list/',{
            }).then(response => {
                this.apiList = response.data;
            })
        },
        exportExcelFile () {
            this.gridOptions.api.exportDataAsExcel({sheetName:'PrelimFile.xlsx'})
        }
    }
};
</script>