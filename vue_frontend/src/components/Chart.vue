<template>
  <v-container>
    <div>
      <highcharts class="chart" :options="localOptions"></highcharts>
      <v-menu v-model="showMenu" :position-x="x" :position-y="y" offset-y
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
                    <v-list-item-title v-text="item.text"></v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card-text> </v-card
      ></v-menu>
    </div>
  </v-container>
</template>

<script>
  import _ from "lodash";
  export default {
    name: "Chart",
    props: ["chartId", "commatize"],
    data: () => ({
      showMenu: false,
      x: 0,
      y: 0,
      drillDowns: [
        { text: "Product Category", value: "product_category" },
        { text: "Customer Type", value: "customer_type" },
      ],
      filters: {},
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

            if (_.isEmpty(this.filters)) {
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
        this.showMenu = false;
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

        this.filters[value] = {
          value: value,
          text: text,
          filter: filter,
        };

        this.x = e.clientX;
        this.y = e.clientY;
        this.showMenu = true;

        // console.log(this.filters);
        // console.log(e);
      },
      getDrillDown(item) {
        this.grouping = item;
        this.getData();
      },
    },
  };
</script>
