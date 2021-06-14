<template>
  <v-container>
    <highcharts class="chart" :options="chartOptions"></highcharts>
  </v-container>
</template>

<script>
  export default {
    name: "PieChart",
    props: ["chartData", "options", "commatize"],
    data: () => ({
      chartOptions: {},
    }),
    beforeMount() {
      this.chartOptions = {
        title: {
          text: this.options.title,
        },
        credits: false,
        chart: {
          type: this.options.type,
          backgroundColor: "transparent",
        },
        tooltip: {
          hideDelay: 0,
          outside: true,
          shared: true,
          pointFormat: `<b>${this.options.prefix}{point.y:,.0f}</b>`,
        },
        series: [],
      };
    },
    watch: {
      chartData(value) {
        this.chartOptions.series = {
          data: value,
        };
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
