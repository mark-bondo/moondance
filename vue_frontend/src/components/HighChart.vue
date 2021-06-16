<template>
  <v-container>
    <highcharts class="chart" :options="localOptions"></highcharts>
  </v-container>
</template>

<script>
  import _ from "lodash";
  export default {
    name: "HighChart",
    props: ["options", "commatize"],
    data: () => ({
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
    // watch: {
    //   chartData(value) {
    //     this.getData(value);
    //   },
    // },
    methods: {
      getData() {
        this.$http
          .post(`get-chart-data/`, {
            data: this.options.sql,
          })
          .then((response) => {
            let data = response.data;
            _.merge(this.localOptions, this.options);

            if (this.chartMap[this.localOptions.chart.type] === "summary") {
              this.localOptions.series = [{ data: data.data, name: data.name }];
              console.log(this.localOptions.series);
            } else if (this.localOptions.xAxis.type === "datetime") {
              this.localOptions.series = this.parseDates(data.data);
            } else {
              this.localOptions.series = data.data;
            }

            // this.localOptions.tooltip.pointFormat =
            //   this.localOptions.chart.type === "summary"
            //     ? "<span>{point.name}</span>: <b>{point.y}</b><br/>"
            //     : "<span>{series.name}</span>: <b>{point.y}</b><br/>";
            // this.chartOptions.title = {
            //   text: `${this.options.title}<br> ${this.options.prefix}${this.commatize(
            //     this.options.total
            //   )}`,
            // };
          });
      },
      createPointEvent() {
        return {
          events: {
            click: (e) => {
              this.drillDown(e);
            },
          },
        };
      },
      parseDates(series) {
        for (let i = 0; i < series.length; i++) {
          var obj = series[i];
          series[i].point = this.createPointEvent();

          for (let x = 0; x < obj.data.length; x++) {
            obj.data[x][0] = Date.parse(obj.data[x][0]);
          }
        }
        return series;
      },
      drillDown(e) {
        if (this.localOptions.chartCategory === "phased") {
          console.log(e.point.series.name);
        } else {
          console.log(e.point.name);
        }
      },
    },
  };
</script>
