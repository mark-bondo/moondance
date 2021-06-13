<template>
  <v-container>
    <highcharts class="chart" :options="chartOptions"></highcharts>
  </v-container>
</template>

<script>
  export default {
    name: "PieChart",
    props: ["title", "type", "chartData", "options", "commatize", "prefix"],
    data: () => ({
      chartOptions: {},
      series: {
        quantity: { color: "#0c5ea2", format: "" },
        sales: { color: "#88075f", format: "$" },
        margin: { color: "#019c15", format: "" },
      },
    }),
    beforeMount() {
      this.chartOptions = {
        title: {
          text: this.title,
        },
        credits: false,
        chart: {
          type: "pie",
          backgroundColor: "transparent",
        },
        tooltip: {
          hideDelay: 0,
          outside: true,
          shared: true,
          // valueDecimals: 0,
          pointFormat: `<b>${this.prefix}{point.y:,.0f}</b>`,
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
          text: this.title,
        };
      },
    },
    methods: {},
  };
</script>
