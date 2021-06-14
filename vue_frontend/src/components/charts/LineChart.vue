<template>
  <v-container>
    <highcharts class="chart" :options="chartOptions"></highcharts>
  </v-container>
</template>

<script>
  export default {
    name: "LineChart",
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
        xAxis: {
          type: "datetime",
          dateTimeLabelFormats: {
            // don't display the dummy year
            month: "%b",
            year: "%Y",
          },
          title: {
            text: "Date",
          },
          // categories: this.xaxis,
        },
        legend: {
          enabled: false,
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
        this.chartOptions.series = value;
        this.chartOptions.title = {
          text: `${this.options.title}<br> ${this.options.prefix}${this.commatize(
            this.options.total
          )}`,
        };
      },
    },
    methods: {},
  };
</script>
