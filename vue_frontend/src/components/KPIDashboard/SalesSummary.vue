<template>
  <v-card>
    <v-card-title>
      <v-row>
        <v-col cols="12"> Sales Summary</v-col>
      </v-row>
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" xs="12" md="6" lg="4">
          <pie-chart
            name="Sales by Sales Channel"
            type="sales"
            :chartData="chart1.data"
            :options="chart1.options"
          />
        </v-col>
        <v-col cols="12" xs="12" md="6" lg="4">
          <pie-chart
            name="Sales by Sales Channel"
            type="sales"
            :chartData="chart1.data"
            :options="chart1.options"
          />
        </v-col>
        <v-col cols="12" xs="12" md="6" lg="4">
          <pie-chart
            name="Sales by Sales Channel"
            type="sales"
            :chartData="chart1.data"
            :options="chart1.options"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
  import PieChart from "@/components/charts/PieChart.vue";

  export default {
    name: "SalesSummary",
    components: {
      PieChart,
    },
    props: [],
    data: function () {
      return {
        gridLoading: true,
        productFamilies: [],
        productData: [],
        search: "",
        expanded: [],
        chart1: {},
      };
    },
    computed: {},
    watch: {},
    beforeMount() {
      this.getPie("sales_channel");
    },
    methods: {
      getPie(value) {
        this.$http
          .get(`../get-pie/${value}`, {
            // data: params
          })
          .then((response) => {
            this.chart1 = response.data;
          });
      },
    },
  };
</script>


<style>
</style>
