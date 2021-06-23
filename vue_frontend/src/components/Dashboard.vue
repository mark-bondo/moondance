<template>
  <v-row>
    <v-col v-for="chartId in charts" :key="chartId" cols="12" xs="12" lg="6">
      <chart :chartId="chartId" />
    </v-col>
  </v-row>
</template>
<script>
  import Chart from "@/components/Chart.vue";
  export default {
    name: "Dashboard",
    components: {
      Chart,
    },
    props: ["charts"],
    data: () => ({
      // chartMenu: [],
      // defaultChartOptions: {},
      // charts: [],
    }),
    beforeMount() {
      // console.log(this.dashboard);
    },
    // watch: {
    //   dashboard() {
    //     this.getSettings();
    //   },
    // },

    // methods: {
    //   async getSettings() {
    //     this.chartMenu = await this.getChartMenu().data;
    //     console.log(1);
    //     this.defaultChartOptions = await this.getdefaultChartOptions().data;
    //     console.log(2);
    //     this.charts = this.dashboard.charts;
    //     console.log(3);
    //   },
    //   getChartMenu() {
    //     return this.$http.get(`default-settings/chartMenu`, {});
    //   },
    //   getdefaultChartOptions() {
    //     return this.$http.get(`default-settings/defaultChartOptions`, {});
    //   },
    // },
  };
</script>


<style>
</style>
