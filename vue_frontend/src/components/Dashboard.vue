<template>
  <div>
    <v-row class="mb-3">
      <v-tabs
        v-show="charts.length !== 0"
        v-model="selectedDate.id"
        centered
        center-active
        color="green"
      >
        <v-tab v-for="d in dateTabs" :key="d.id">{{ d.text }}</v-tab>
      </v-tabs>
    </v-row>
    <v-row>
      <v-col v-for="chartId in charts" :key="chartId" cols="12" xs="12" lg="6">
        <chart :chartId="chartId" :selectedDate="selectedDate" />
      </v-col>
    </v-row>
  </div>
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
      dateTabs: [
        { id: 1, text: "Today" },
        { id: 2, text: "This Week" },
        { id: 3, text: "This Month" },
        { id: 4, text: "This Year" },
        { id: 5, text: "All Dates" },
      ],
      selectedDate: { id: 2, text: "This Week" },
    }),
  };
</script>


<style>
</style>
