<template>
  <v-container>
    <highcharts class="chart" :options="chartOptions"></highcharts>
  </v-container>
</template>

<script>
  export default {
    name: "HighChart",
    props: ["chartData", "options", "commatize"],
    data: () => ({
      chartOptions: {},
    }),
    beforeMount() {
      this.chartOptions = {
        title: {
          text: "",
        },
        credits: false,
        chart: {
          type: this.options.type,
          backgroundColor: "transparent",
          // width: 160,
          // height: 65,
          // margin: [0, 0, 4, 0],
          // style: {
          //   overflow: "visible",
          // },
        },
        legend: {
          enabled: true,
        },
        tooltip: {
          hideDelay: 0,
          outside: true,
          shared: true,
          pointFormat: `<span>{series.name}</span>: <b>${this.options.prefix}{point.y}<br/>`,
        },
        series: [],
      };
    },
    watch: {
      chartData(value) {
        this.updateChart(value);
      },
    },
    methods: {
      createPointEvent() {
        return {
          events: {
            click: (e) => {
              this.drillDown(e);
            },
          },
        };
      },
      updateChart(value) {
        if (this.options.chartCategory === "phased") {
          this.chartOptions.xAxis = {
            type: "datetime",
            dateTimeLabelFormats: {
              month: "%b %Y",
              year: "%Y",
            },
            title: {
              text: "Date",
            },
          };
          this.chartOptions.series = this.parseDates(value);
        } else {
          this.chartOptions.series = {
            data: value,
            point: Object.assign(this.createPointEvent()),
          };
        }

        this.chartOptions.title = {
          text: `${this.options.title}<br> ${this.options.prefix}${this.commatize(
            this.options.total
          )}`,
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
        if (this.options.chartCategory === "phased") {
          console.log(e.point.series.name);
        } else {
          console.log(e.point.name);
        }
      },
    },
  };
</script>
