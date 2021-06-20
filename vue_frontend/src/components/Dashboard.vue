<template>
  <v-row>
    <v-col
      v-for="chartId in dashboard.charts"
      :key="chartId"
      cols="12"
      xs="12"
      lg="6"
    >
      <chart :chartId="chartId" :dashboardId="dashboard.id" />
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
    props: ["dashboard"],
    data: function () {
      return {};
    },
  };
</script>


<style>
</style>
