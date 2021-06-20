<template>
  <v-row>
    <v-col
      v-for="chartId in charts"
      :key="chartId"
      cols="12"
      xs="12"
      lg="6"
      class="pa-0"
    >
      <chart :chartId="chartId" :dashboardId="dashboardId" />
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
    props: ["dashboardId"],
    data: function () {
      return {
        // charts: [],
      };
    },
    computed: {
      charts() {
        return this.$store.state.kpi.dashboard[this.dashboardId].charts;
      },
    },
    watch: {},
    beforeMount() {},
    methods: {},
  };
</script>


<style>
</style>
