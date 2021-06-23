<template>
  <v-card>
    <v-card-title class="justify-center pa-0">
      <v-toolbar dense dark color="#554e6e">
        <v-spacer></v-spacer>
        <v-toolbar-title>{{ extraOptions.title }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-menu left offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" v-on="on">
              <v-icon>mdi-chart-box-outline</v-icon>
            </v-btn>
          </template>
          <v-list-item-group
            v-model="extraOptions.selectedChartType"
            active-class="deep-purple--text text--accent-4"
          >
            <v-list>
              <v-list-item
                v-for="c in chartMenu"
                :key="c.type"
                @click="changeChartType(c)"
              >
                <v-list-item-icon
                  ><v-icon v-text="c.icon"></v-icon
                ></v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title> {{ c.type }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-list-item-group>
        </v-menu>
      </v-toolbar>
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" class="pa-0">
          <bread-crumbs
            :AvailableDrillDowns="AvailableDrillDowns"
            :selectedBreadCrumb="selectedBreadCrumb"
            :drillDowns="drillDowns"
            :selectedFilterValue="selectedFilterValue"
            :activeIconMap="activeIconMap"
            @updateDrillDowns="updateDrillDowns"
          >
          </bread-crumbs>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" v-if="localOptions">
          <highcharts :options="localOptions"></highcharts>
          <drill-menu
            :AvailableDrillDowns="AvailableDrillDowns"
            :showDrillMenu="showDrillMenu"
            :chartCategory="extraOptions.chartCategory"
            @setParentItem="setParentItem"
          ></drill-menu>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
  import _ from "lodash";
  import BreadCrumbs from "@/components/BreadCrumbs.vue";
  import DrillMenu from "@/components/DrillMenu.vue";

  export default {
    name: "Chart",
    props: ["chartId"],
    components: { BreadCrumbs, DrillMenu },
    data: () => ({
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
      showDrillMenu: null,
      drillDowns: [],
      selectedFilterValue: null,
      selectedBreadCrumb: null,
      extraOptions: {
        title: "Loading Chart",
        selectedChartType: null,
      },
      chartMenu: [],
      localOptions: {},
      isInitialLoad: true,
    }),
    computed: {
      AvailableDrillDowns() {
        return _.sortBy(
          this.drillDowns.filter((d) => d.isBreadCrumb === false),
          "text"
        );
      },
    },
    beforeMount() {
      this.getSettings();
    },
    methods: {
      async getSettings() {
        this.chartMenu = (
          await this.$http.get(`default-settings/chartMenu`, {})
        ).data;
        this.localOptions = (
          await this.$http.get(`default-settings/defaultChartOptions`, {})
        ).data;
        this.getData();
      },

      changeChartType(item) {
        this.selectedChartType = item.type;
        this.localOptions.chart.type = item.type;

        if (item.category !== this.extraOptions.chartCategory) {
          this.extraOptions.chartCategory = item.category;
          this.getData();
        } else {
          this.extraOptions.chartCategory = item.category;
        }
      },
      getData() {
        this.localOptions.series = [];
        this.$http
          .post(`chart/${this.chartId}`, {
            filters: _.reject(this.drillDowns, { filter: null }),
            grouping: _.find(this.drillDowns, { isCurrent: true }),
            chartCategory: this.extraOptions.chartCategory,
          })
          .then((response) => {
            let serverOptions = response.data.highCharts;
            this.extraOptions = response.data.extraOptions;

            if (this.isInitialLoad) {
              this.drillDowns = this.extraOptions.drillDowns;
              this.drillDowns.forEach(
                (d) => (d.icon = this.activeIconMap[d.isCurrent])
              );

              _.merge(this.localOptions, serverOptions);
              this.localOptions.series = [];
            }

            this.parseSeries(serverOptions.series);
            this.isInitialLoad = false;
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
              this.showDrillMenu = e;
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
      updateDrillDowns(d) {
        this.drillDowns = d;
        this.getData();
      },
      setParentItem(item) {
        this[item.name] = item.value;
      },
    },
  };
</script>
