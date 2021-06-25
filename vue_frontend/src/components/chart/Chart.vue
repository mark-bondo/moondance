<template>
  <v-card>
    <v-card-title class="justify-center pa-0">
      <chart-toolbar
        :extraOptions="extraOptions"
        :localOptions="localOptions"
        :fields="fields"
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
        <v-col cols="12">
          <highcharts
            :options="localOptions"
            v-if="!isInitialLoad"
          ></highcharts>
          <drill-menu
            :drillItems="drillItems"
            :selectedDrillItem="selectedDrillItem"
            :chartCategory="extraOptions.chartCategory"
            @setParentItem="setParentItem"
          ></drill-menu>
        </v-col>

        <v-overlay :absolute="true" :value="isLoading">
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

  export default {
    name: "Chart",
    props: ["chartId", "dateFilter"],
    components: { BreadCrumbs, DrillMenu, ChartToolbar },
    data: () => ({
      isInitialLoad: true,
      isLoading: true,
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
      drillItems() {
        return _.sortBy(
          this.fields.filter((d) => d.isBreadCrumb === false),
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
            grouping: _.find(this.fields, { isCurrent: true }),
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

            this.parseSeries(serverOptions.series);
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
      setParentItem(item) {
        this[item.name] = item.value;

        if (item.refreshData) {
          this.getData();
        }
      },
    },
  };
</script>
<style>
</style>
