<template>
  <v-container>
    <v-card>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-breadcrumbs :items="breadCrumbs">
              <template v-slot:item="{ item }">
                <v-breadcrumbs-item>
                  <v-icon>mdi-filter</v-icon>
                  {{ item.filter }}
                </v-breadcrumbs-item>
              </template>
              <template v-slot:divider>
                <v-icon>mdi-chevron-right</v-icon>
              </template>
            </v-breadcrumbs>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <highcharts class="chart" :options="localOptions"></highcharts>
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
                        v-for="item in drillDowns"
                        :key="item.value"
                        @click="getDrillDown(item)"
                      >
                        <v-list-item-content>
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
  export default {
    name: "Chart",
    props: ["chartId", "commatize"],
    data: () => ({
      menu: {
        show: false,
        x: 0,
        y: 0,
      },
      breadCrumbs: [],
      drillDowns: [
        { text: "Product Category", value: "product_category" },
        { text: "Customer Type", value: "customer_type" },
      ],
      filters: [],
      grouping: { value: null, text: null },
      chartMap: {
        pie: "summary",
        donut: "summary",
        area: "phased",
        line: "phased",
        spline: "phased",
        column: "phased",
        bar: "phased",
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
          shared: true,
          pointFormat: "<b>{point.y}</b><br/>",
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
    beforeMount() {},
    mounted() {
      this.getData();
    },
    methods: {
      getData() {
        this.$http
          .post(`chart/${this.chartId}`, {
            data: Object.assign(
              { filters: this.filters },
              { grouping: this.grouping.value }
            ),
          })
          .then((response) => {
            let serverOptions = response.data;
            if (serverOptions.chart.category === "phased") {
              serverOptions.series = this.parseDates(serverOptions.series);
            }
            serverOptions.series.forEach(
              (s) => (s.point = this.createPointEvent())
            );

            if (this.filters.length === 0) {
              _.merge(this.localOptions, serverOptions);
            } else {
              this.localOptions.series = serverOptions.series;
            }
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
        var filter;
        var value;
        var text;

        if (this.localOptions.chart.category === "phased") {
          filter = e.point.series.name;
        } else {
          filter = e.point.name;
          value = e.point.series.userOptions.value;
          text = e.point.series.userOptions.name;
        }

        this.filters.push({
          value: value,
          text: text,
          filter: filter,
        });

        this.menu = {
          x: e.clientX,
          y: e.clientY,
          show: true,
        };

        // console.log(this.filters);
        // console.log(e);
      },
      getDrillDown(item) {
        this.grouping = item;
        this.breadCrumbs = _.clone(this.filters);
        this.getData();
      },
    },
  };
</script>
