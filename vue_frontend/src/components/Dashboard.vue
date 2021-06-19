<template>
  <v-card height="calc(100% - 86.19px)">
    <v-card-title>
      <!-- <v-row>
        <v-col cols="12"> Sales Summary</v-col>
      </v-row> -->
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col
          v-for="chartId in charts"
          :key="chartId"
          cols="12"
          xs="12"
          lg="6"
        >
          <chart :chartId="chartId" :dashboardId="dashboardId" />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
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
