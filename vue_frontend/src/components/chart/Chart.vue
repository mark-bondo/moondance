<template>
  <v-card>
    <v-card-title class="justify-center pa-0">
      <chart-toolbar
        :extraOptions="extraOptions"
        :chartTypeChoices="chartTypeChoices"
        @setChartType="setChartType"
      >
      </chart-toolbar>
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" class="pa-0">
          <bread-crumbs
            :drillItems="drillItems"
            :selectedBreadCrumb="selectedBreadCrumb"
            :fields="fields"
            :selectedFilterValue="selectedFilterValue"
            :activeIconMap="activeIconMap"
            @setFields="setFields"
          >
          </bread-crumbs>
        </v-col>
      </v-row>
      <v-row>
        <v-col v-if="extraOptions.chartCategory !== 'table'">
          <v-row>
            <v-col>
              <highcharts
                style="
                  min-width: 400px;
                  min-height: 400px;
                  height: 100%;
                  width: 100%;
                "
                :options="localOptions"
                v-if="!isInitialLoad"
              ></highcharts>
              <drill-menu
                :drillItems="drillItems"
                :selectedDrillItem="selectedDrillItem"
                :chartCategory="extraOptions.chartCategory"
                @setBreadCrumb="setBreadCrumb"
                @setFilterValue="setFilterValue"
              ></drill-menu>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12" v-else-if="extraOptions.chartCategory == 'table'">
          <ag-grid-vue
            style="
              min-width: 400px;
              min-height: 400px;
              height: 100%;
              width: 100%;
            "
            class="ag-theme-alpine"
            :columnDefs="columnDefs"
            :defaultColDef="defaultColDef"
            :rowData="localOptions.series"
            :enableRangeSelection="true"
            :applyColumnDefOrder="true"
          >
          </ag-grid-vue>
        </v-col>
        <v-col v-else>
          <div
            style="
              min-width: 400px;
              min-height: 400px;
              height: 100%;
              width: 100%;
            "
          ></div>
        </v-col>
        <v-overlay
          :absolute="true"
          :value="isLoading"
          style="
            min-width: 400px;
            min-height: 400px;
            height: 100%;
            width: 100%;
            display: flex;
            flex-direction: column;
          "
        >
          <v-progress-circular
            indeterminate
            :size="70"
            :width="7"
            color="deep-purple"
          ></v-progress-circular
        ></v-overlay>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
  import _ from "lodash";
  import BreadCrumbs from "@/components/chart/BreadCrumbs.vue";
  import DrillMenu from "@/components/chart/DrillMenu.vue";
  import ChartToolbar from "@/components/chart/ChartToolbar.vue";

  import { AgGridVue } from "ag-grid-vue";
  // import "ag-grid-enterprise";

  export default {
    name: "Chart",
    props: ["chartId", "dateFilter"],
    components: { BreadCrumbs, DrillMenu, ChartToolbar, AgGridVue },
    data: () => ({
      isInitialLoad: true,
      isLoading: true,
      defaultColDef: {
        resizable: true,
        sortable: true,
        suppressMenu: true,
        floatingFilter: true,
      },
      localOptions: {},
      extraOptions: {},
      chartTypeChoices: [],
      fields: [],
      selectedDrillItem: null,
      selectedFilterValue: null,
      selectedBreadCrumb: null,
      activeIconMap: {
        true: {
          current: "mdi-eye-outline",
          color: "success",
        },
        false: {
          current: "mdi-filter-outline",
          color: "grey",
        },
      },
    }),
    computed: {
      columnDefs() {
        var fields = [];
        var self = this;

        _.forEach(_.sortBy(this.fields, "type"), function (f) {
          if (f.isCurrent === true && f.type !== "xaxis") {
            var field = { headerName: f.text, field: f.value };

            switch (f.type) {
              case "grouping":
                field.filter = "agTextColumnFilter";
                break;
              case "yaxis":
                field.filter = "agNumberColumnFilter";
                field.type = "rightAligned";
                field.valueFormatter = (params) =>
                  self.currencyFormatter(params.value, self.extraOptions.prefix);
                break;
              case "xaxis":
                field.filter = "agDateColumnFilter";
                break;
            }

            fields.push(field);
          }
        });
        return fields;
      },
      drillItems() {
        return _.sortBy(
          _.filter(this.fields, { isBreadCrumb: false, type: "grouping" }),
          "text"
        );
      },
    },
    watch: {
      dateFilter() {
        this.getData();
      },
    },
    beforeMount() {
      this.getSettings();
    },
    methods: {
      async getSettings() {
        this.chartTypeChoices = (
          await this.$http.get(`default-settings/chartTypeChoices`, {})
        ).data;
        this.localOptions = (
          await this.$http.get(`default-settings/defaultChartOptions`, {})
        ).data;
        this.getData();
      },
      currencyFormatter(currency, sign) {
        var sansDec = currency.toFixed(0);
        var formatted = sansDec.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        return sign + `${formatted}`;
      },
      getData() {
        this.isLoading = true;
        this.localOptions.series = [];
        var filters = _.reject(this.fields, { filter: null });

        filters.push({
          value: this.extraOptions.xAxis,
          filter: this.dateFilter,
          type: "xaxis",
        });

        this.$http
          .post(`chart/${this.chartId}`, {
            filters: filters,
            grouping: _.find(this.fields, { isCurrent: true, type: "grouping" }),
            chartCategory: this.extraOptions.chartCategory,
          })
          .then((response) => {
            let serverOptions = response.data.highCharts;
            this.extraOptions = response.data.extraOptions;

            if (this.isInitialLoad) {
              this.fields = this.extraOptions.fields;
              this.fields.forEach(
                (d) => (d.icon = this.activeIconMap[d.isCurrent])
              );

              _.merge(this.localOptions, serverOptions);
              this.localOptions.series = [];
            }

            if (this.extraOptions.chartCategory !== "table") {
              this.parseSeries(serverOptions.series);
            } else {
              this.localOptions.series = serverOptions.series;
            }
            this.isInitialLoad = false;
            this.isLoading = false;
          });
      },
      parseSeries(series) {
        let self = this;
        series =
          this.extraOptions.chartCategory === "phased"
            ? this.parseDates(series)
            : series;

        _.forEach(series, function (s) {
          self.localOptions.series.push(
            Object.assign(s, { point: self.createPointEvent() })
          );
        });
      },
      createPointEvent() {
        return {
          events: {
            click: (e) => {
              this.selectedDrillItem = e;
            },
          },
        };
      },
      parseDates(series) {
        for (let i = 0; i < series.length; i++) {
          var obj = series[i];

          for (let x = 0; x < obj.data.length; x++) {
            obj.data[x][0] = Date.parse(obj.data[x][0]);
          }
        }
        return series;
      },
      setFields(d) {
        this.fields = d;
        this.getData();
      },
      setChartType(item) {
        this.localOptions.chart.type = item.type;
        this.extraOptions.chartCategory = item.category;

        if (item.refreshData) {
          this.getData();
        }
      },
      setFilterValue(item) {
        this.selectedFilterValue = item;
      },
      setBreadCrumb(item) {
        this.selectedBreadCrumb = item;
      },
    },
  };
</script>
<style type="sass">
  .vert-text {
    transform: rotate(-90deg);
  }
</style>
