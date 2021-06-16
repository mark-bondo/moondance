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
          <high-chart :options="chart" :commatize="commatize" />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
  import HighChart from "@/components/HighChart.vue";

  export default {
    name: "Dashboard",
    components: {
      HighChart,
    },
    props: ["commatize"],
    data: function () {
      return {
        charts: [],
      };
    },
    computed: {},
    watch: {},
    beforeMount() {
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
