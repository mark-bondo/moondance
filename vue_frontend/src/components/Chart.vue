<template>
  <v-container>
    <v-card>
      <v-card-title class="justify-center">{{
        extraOptions.title
      }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" class="pa-0">
            <bread-crumbs
              :getData="getData"
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
                <v-card-text>
                  <v-list dense>
                    <v-subheader>Drill Down</v-subheader>
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
                  </v-list>
                </v-card-text> </v-card
            ></v-menu>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
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
          color: "green",
        },
        false: {
          current: "mdi-filter-outline",
          color: "grey",
        },
      },
      drillDowns: [],
      selectedFilterValue: null,
      addedBreadCrumb: null,
      extraOptions: {
        title: "Loading Chart",
      },
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
        return this.drillDowns.filter((d) => d.isBreadCrumb === false);
      },
    },
    beforeMount() {
      this.chartStore = this.$store.state.kpi.dashboard[this.dashboardId][
        this.chartId
      ] = {};
      this.getData();
    },
    methods: {
      getData() {
        this.localOptions.series = [];
        this.$http
          .post(`chart/${this.chartId}`, {
            filters: _.reject(this.drillDowns, { filter: null }),
            grouping: _.find(this.drillDowns, { isCurrent: true }),
          })
          .then((response) => {
            let serverOptions = response.data.highCharts;
            this.extraOptions = response.data.extraOptions;

            if (this.drillDowns.length === 0) {
              this.drillDowns = this.extraOptions.drillDowns;
              this.drillDowns.forEach(
                (d) => (d.icon = this.iconMap[d.isCurrent])
              );
            }

            if (this.extraOptions.category === "phased") {
              serverOptions.series = this.parseDates(serverOptions.series);
            }

            serverOptions.series.forEach(
              (s) => (s.point = this.createPointEvent())
            );

            _.merge(this.localOptions, serverOptions);
            this.localOptions.series = [];
            this.localOptions.plotOptions = Object.assign(
              {},
              this.localOptions.plotOptions
            );
            serverOptions.series.forEach((s) => this.localOptions.series.push(s));
            this.chartStore.drillDowns = this.drillDowns;
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
          this.extraOptions.category === "phased"
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
        this.getData();
      },
      updateDrillDowns(d) {
        // console.log(d);
        // console.log(this.drillDowns);
        // console.log(_.intersectionWith(d, this.drillDowns, _.isEqual));

        this.drillDowns = d;
        this.getData();
      },
    },
  };
</script>
