<template>
  <v-card>
    <v-card-title>
      <v-row>
        <v-col cols="12"> Sales Summary</v-col>
      </v-row>
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col
          v-for="chart in charts"
          :key="chart.id"
          cols="12"
          xs="12"
          md="6"
          lg="4"
        >
          <div v-if="chart.options.type === 'pie'">
            <pie-chart
              :chartData="chart.data"
              :options="chart.options"
              :commatize="commatize"
            />
          </div>
          <div v-else-if="chart.options.type === 'spline'">
            <line-chart
              :chartData="chart.data"
              :options="chart.options"
              :commatize="commatize"
            />
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
  import PieChart from "@/components/charts/PieChart.vue";
  import LineChart from "@/components/charts/LineChart.vue";

  export default {
    name: "SalesSummary",
    components: {
      PieChart,
      LineChart,
    },
    props: ["commatize"],
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
          // {
          //   id: 2,
          //   sql: {
          //     group: "product_family",
          //     xaxis: null,
          //     yaxis: "net_sales",
          //     filters: "",
          //   },
          //   options: {
          //     title: "Product Family Sales",
          //     type: "pie",
          //     prefix: "$",
          //   },
          //   data: [],
          // },
          {
            id: 3,
            sql: {
              group: "source_system",
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

          // {
          //   title: "Sales By Month",
          //   type: "spline",
          //   prefix: "$",
          //   group: "sales_channel",
          //   xaxis: "processed_date",
          //   yaxis: "net_sales",
          //   filters: "",
          //   data: [],
          // },
        ],
      };
    },
    computed: {},
    watch: {},
    beforeMount() {
      this.charts.forEach((chart) => {
        this.getData(chart);
      });
    },
    methods: {
      getData(chart) {
        var params = Object.assign(chart.sql, { type: chart.options.type });
        this.$http
          .post(`get-chart-data/`, {
            data: params,
          })
          .then((response) => {
            chart.data = response.data.data;
            Object.assign(chart.options, response.data.options);
          });
      },
    },
  };
</script>


<style>
</style>
