<template>
  <v-card>
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
            :options="chart.options"
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
        charts: [
          {
            id: 1,
            sql: {
              group: "sales_channel",
              xaxis: null,
              yaxis: "net_sales",
              filters: "",
            },
            options: {
              title: "Sales Channel Sales",
              type: "pie",
              prefix: "$",
            },
            data: [],
          },
          {
            id: 3,
            sql: {
              group: "sales_channel",
              xaxis: "processed_period",
              yaxis: "net_sales",
              filters: "",
            },
            options: {
              title: "Product Family Sales by Month",
              type: "spline",
              prefix: "$",
            },
            data: [],
          },
        ],
      };
    },
    computed: {},
    watch: {},
    beforeMount() {
      this.charts.forEach((chart) => {
        this.getChartData(chart);
      });
    },
    methods: {
      // getData(chart) {
      //   var params = Object.assign(chart.sql, { type: chart.options.type });
      //   this.$http
      //     .post(`get-chart-data/`, {
      //       data: params,
      //     })
      //     .then((response) => {
      //       chart.data = response.data.data;
      //       chart.options.chartCategory =
      //         this.chartCategories[chart.options.type];
      //       Object.assign(chart.options, response.data.options);
      //     });
      // },
    },
  };
</script>


<style>
</style>
