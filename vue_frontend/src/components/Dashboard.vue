<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-tabs
          v-show="charts.length !== 0"
          v-model="dateFilter"
          centered
          show-arrows
          center-active
          color="green"
        >
          <v-tab v-for="(item, index) in dateTabs" :key="index">{{
            item
          }}</v-tab>
        </v-tabs>
      </v-col>
    </v-row>
    <v-row>
      <v-col v-for="chartId in charts" :key="chartId" cols="12" xs="12" lg="6">
        <chart :chartId="chartId" :dateFilter="dateTabs[dateFilter]" />
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
  import Chart from "@/components/chart/Chart.vue";
  export default {
    name: "Dashboard",
    components: {
      Chart,
    },
    props: ["charts"],
    data: () => ({
      dateTabs: [
        "Today",
        "This Week",
        "This Month",
        "This Quarter",
        "This Year",
        "All Dates",
      ],
      dateFilter: 2,
    }),
  };
</script>


<style>
</style>
