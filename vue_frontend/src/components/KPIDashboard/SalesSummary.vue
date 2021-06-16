<template>
  <v-card height="calc(100% - 86.19px)">
    <v-card-title>
      <v-row>
        <v-col cols="12"> Sales Summary</v-col>
      </v-row>
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col v-for="chart in charts" :key="chart.id" cols="12" xs="12" lg="6">
          <high-chart
            :chartData="chart.data"
            :options="chart.chartOptions"
            :commatize="commatize"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
  import HighChart from "@/components/HighChart.vue";

  export default {
    name: "SalesSummary",
    components: {
      HighChart,
    },
    props: ["commatize", "getChartData"],
    data: function () {
      return {
        gridLoading: true,
        charts: [],
        // charts: [
        //   {
        //     id: 1,
        //     sql: {
        //       group: "sales_channel",
        //       xaxis: null,
        //       yaxis: "net_sales",
        //       filters: "",
        //     },
        //     chartOptions: {
        //       title: "Sales Channel Sales",
        //       type: "pie",
        //       prefix: "$",
        //     },
        //     data: [],
        //   },
        //   {
        //     id: 2,
        //     sql: {
        //       group: "sales_channel",
        //       xaxis: "processed_period",
        //       yaxis: "net_sales",
        //       filters: "",
        //     },
        //     chartOptions: {
        //       title: "Product Family Sales by Month",
        //       type: "spline",
        //       prefix: "$",
        //       xAxis: {
        //         title: { text: "Date Ordered" },
        //         type: "datetime",
        //         dateTimeLabelFormats: {
        //           month: "%b %Y",
        //           year: "%Y",
        //         },
        //       },
        //       legend: {
        //         enabled: true,
        //       },
        //     },
        //     data: [],
        //   },
        // ],
      };
    },
    computed: {},
    watch: {},
    beforeMount() {
      // this.charts.forEach((chart) => {
      //   this.getChartData(chart);
      // });
      this.charts = this.getDashboard(1);
    },
    methods: {
      getDashboard(id) {
        this.$http.get(`../dashboard/${id}`, {}).then((response) => {
          this.charts = response.data.charts;
        });
      },
    },
  };
</script>


<style>
</style>
