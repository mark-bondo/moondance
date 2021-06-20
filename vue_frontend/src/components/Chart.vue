<template>
  <v-card height="100%">
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
            :addedBreadCrumb="addedBreadCrumb"
            :drillDowns="drillDowns"
            :selectedFilterValue="selectedFilterValue"
            @updateDrillDowns="updateDrillDowns"
          >
          </bread-crumbs>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="pa-0">
          <highcharts
            ref="chartComponent"
            class="chart"
            :options="localOptions"
          ></highcharts>
          <v-menu
            v-model="menu.show"
            :position-x="menu.x"
            :position-y="menu.y"
            offset-y
            ><v-card>
              <v-card-text class="pa-1">
                <v-list dense>
                  <v-subheader>Drill Down Options</v-subheader>
                  <v-list-item-group color="primary">
                    <v-list-item
                      v-for="item in AvailableDrillDowns"
                      :key="item.value"
                      @click="drillDownSelected(item)"
                    >
                      <v-list-item-content v-if="item.isBreadCrumb === false">
                        <v-list-item-title
                          v-text="item.text"
                        ></v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list-item-group>
                  <v-divider></v-divider>
                </v-list>
              </v-card-text> </v-card
          ></v-menu>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
  import _ from "lodash";
  import BreadCrumbs from "@/components/BreadCrumbs.vue";

  export default {
    name: "Chart",
    props: ["chartId", "dashboardId"],
    components: { BreadCrumbs },
    data: () => ({
      menu: {
        show: false,
        x: 0,
        y: 0,
      },
      iconMap: {
        true: {
          current: "mdi-eye-outline",
          color: "success",
        },
        false: {
          current: "mdi-filter-outline",
          color: "grey",
        },
      },
      chartMenu: [
        {
          category: "summary",
          type: "pie",
          icon: "mdi-chart-pie",
          isActive: true,
        },
        // {
        //   category: "summary",
        //   type: "donut",
        //   icon: "mdi-chart-donut",
        //   isActive: false,
        // },
        {
          category: "phased",
          type: "area",
          icon: "mdi-chart-areaspline-variant",
          isActive: false,
        },
        {
          category: "phased",
          type: "line",
          icon: "mdi-chart-line",
          isActive: false,
        },
        {
          category: "phased",
          type: "spline",
          icon: "mdi-chart-bell-curve-cumulative",
          isActive: false,
        },
        {
          category: "phased",
          type: "bar",
          icon: "mdi-chart-gantt",
          isActive: false,
        },
        {
          category: "phased",
          type: "column",
          icon: "mdi-chart-bar",
          isActive: false,
        },
      ],
      drillDowns: [],
      selectedFilterValue: null,
      addedBreadCrumb: null,
      extraOptions: {
        title: "Loading Chart",
        selectedChartType: null,
      },
      isInitialLoad: true,
      localOptions: {
        title: {
          text: "",
        },
        credits: false,
        chart: {
          backgroundColor: "transparent",
          style: {
            overflow: "visible",
          },
          type: null,
          height: "50%",
        },
        tooltip: {
          hideDelay: 0,
          outside: true,
          shared: false,
          valueDecimals: 0,
          pointFormat: "{series.name}: <b>{point.y}</b><br/>",
        },
        plotOptions: {
          pie: {
            dataLabels: {
              enabled: true,
              format:
                "<b>{point.name}</b><br>{point.y:,.0f} ({point.percentage:.1f}%)",
            },
          },
        },
        legend: {
          enabled: true,
        },
        xAxis: {
          dateTimeLabelFormats: {
            month: "%b %Y",
            year: "%Y",
          },
        },
        series: [],
      },
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
      this.chartStore = this.$store.state.kpi.dashboard[this.dashboardId][
        this.chartId
      ] = {};
      this.getData();
    },
    methods: {
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
                (d) => (d.icon = this.iconMap[d.isCurrent])
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
              this.showDrillMenu(e);
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
      showDrillMenu(e) {
        this.menu.show = false;

        this.selectedFilterValue =
          this.extraOptions.chartCategory === "phased"
            ? e.point.series.name
            : (this.selectedFilterValue = e.point.name);

        this.menu = {
          x: e.clientX,
          y: e.clientY,
          show: true,
        };
      },
      drillDownSelected(newItem) {
        this.addedBreadCrumb = newItem;
      },
      updateDrillDowns(d) {
        this.drillDowns = d;
        this.getData();
      },
    },
  };
</script>
