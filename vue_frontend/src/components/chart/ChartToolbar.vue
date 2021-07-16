<template>
  <v-toolbar dense class="elevation-0">
    <v-spacer></v-spacer>

    <v-toolbar-text>
      <span>
        {{ extraOptions.yAxis.title.text }}
      </span>
      <span> by </span>
      <span>
        {{ extraOptions.xAxis.title.text }}
      </span>
      <span> {{ extraOptions.total }} </span>
    </v-toolbar-text>
    <v-spacer></v-spacer>
    <v-menu left offset-y>
      <template v-slot:activator="{ on, attrs }">
        <v-btn icon v-bind="attrs" v-on="on" dark color="success">
          <v-icon large>mdi-chart-box</v-icon>
        </v-btn>
      </template>
      <v-list-item-group
        v-model="selectedChartType"
        active-class="deep-purple--text text--accent-4"
      >
        <v-list>
          <v-list-item v-for="c in chartTypeChoices" :key="c.type" :value="c">
            <v-list-item-icon
              ><v-icon v-text="c.icon"></v-icon
            ></v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title> {{ c.type }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-list-item-group>
    </v-menu>
  </v-toolbar>
</template>

<script>
  export default {
    name: "Chart",
    props: ["chartTypeChoices", "extraOptions"],
    data: () => ({
      selectedChartType: {},
    }),
    watch: {
      selectedChartType(item) {
        if (item.category !== this.extraOptions.chartCategory) {
          this.$emit("setChartType", {
            type: item.type,
            category: item.category,
            refreshData: true,
          });
        } else {
          this.$emit("setChartType", {
            type: item.type,
            category: item.category,
            refreshData: false,
          });
        }
      },
    },
    methods: {},
  };
</script>
<style>
  .chip-header {
    height: 35px !important;
  }
</style>

