<template>
  <v-container>
    <highcharts class="chart" :options="chartOptions"></highcharts>
  </v-container>
</template>

<script>
  export default {
    name: "PieChart",
    props: ["name", "type", "chartData", "options"],
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
          text: "",
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
          valueDecimals: 0,
          pointFormat: `<span>${this.name}</span>: <b>
                                        ${this.series[this.type].format}
                                        {point.y}<br/>
                                        `,
        },
        series: [],
      };
    },
    watch: {
      chartData(value) {
        this.chartOptions.series = {
          name: this.name,
          data: value,
        };
        this.chartOptions.title = {
          text: `${this.series[this.type].format}${this.options.total}`,
        };
      },
    },
    methods: {},
  };
</script>
