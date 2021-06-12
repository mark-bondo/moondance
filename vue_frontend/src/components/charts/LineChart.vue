<template>
  <v-container>
    <highcharts class="chart" :options="chartOptions"></highcharts>
  </v-container>
</template>

<script>
  export default {
    name: "LineChart",
    props: ["name", "type", "chartData", "xaxis"],
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
          width: 160,
          height: 65,
          type: "area",
          margin: [0, 0, 4, 0],
          backgroundColor: "transparent",
          style: {
            overflow: "visible",
          },
        },
        xAxis: {
          categories: this.xaxis,
        },
        legend: {
          enabled: false,
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
        series: [
          {
            name: this.type,
            data: this.chartData,
            color: this.series[this.type].color,
          },
        ],
      };
    },
    watch: {
      // name() {
      //   this.v_name = this.name;
      // },
    },
    methods: {},
  };
</script>
