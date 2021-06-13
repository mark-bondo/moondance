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
          <div v-if="chart.type === 'pie'">
            <pie-chart
              type="sales"
              :title="chart.title"
              :chartData="chart.data"
              :options="chart.options"
              :prefix="chart.prefix"
              :commatize="commatize"
            />
          </div>
          <div v-else-if="chart.type === 'spline'">
            <line-chart
              type="margin"
              :title="chart.title"
              :chartData="chart.data"
              :xaxis="chart.xaxis"
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
          {
            id: 1,
            title: "Sales By Sales Channel",
            type: "pie",
            prefix: "$",
            group: "sales_channel",
            xaxis: null,
            yaxis: "net_sales",
            filters: "",
            data: [],
          },
          {
            id: 2,
            title: "Sales By Product Family",
            type: "pie",
            prefix: "$",
            group: "product_family",
            xaxis: null,
            yaxis: "net_sales",
            filters: "",
            data: [],
          },
        ],
      };
    },
    computed: {},
    watch: {},
    beforeMount() {
      this.charts.forEach((d) => {
        this.getData(d);
      });
    },
    methods: {
      getData(d) {
        this.$http
          .post(`get-chart-data/`, {
            data: d,
          })
          .then((response) => {
            let r = response.data;
            d.data = r.data;
            d.title = `${d.title}<br> ${d.prefix}${this.commatize(
              response.data.options.total
            )}`;
          });
      },
    },
  };
</script>


<style>
</style>
