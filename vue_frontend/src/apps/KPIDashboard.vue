<template>
  <v-app>
    <v-card height="100%">
      <v-app-bar
        color="#554e6e"
        dark
        style="height: 86.19px; border-radius: 0px"
      >
        <v-app-bar-nav-icon
          @click.stop="drawer = !drawer"
          style="margin-top: 20px"
        ></v-app-bar-nav-icon>

        <!-- <v-spacer></v-spacer> -->
        <!-- <img
          src="/static/site-wide/logo-large-white.png"
          width="300px"
          style="margin-top: 28px"
          class="d-none d-md-flex"
        /> -->
        <v-spacer></v-spacer>
        <v-toolbar-title style="margin-top: 20px"
          ><h2>{{ title }}</h2></v-toolbar-title
        >

        <v-spacer></v-spacer>

        <!-- <v-btn icon>
          <v-icon>mdi-magnify</v-icon>
        </v-btn>
        <v-btn icon>
          <v-icon>mdi-filter</v-icon>
        </v-btn> -->
      </v-app-bar>

      <v-navigation-drawer v-model="drawer" absolute bottom temporary>
        <v-list>
          <v-list-item-group
            v-model="selectedItem"
            active-class="deep-purple--text text--accent-4"
          >
            <v-list-item v-for="d in dashboards" :key="d.id" :value="d.name">
              <v-list-item-content>
                <v-list-item-title v-text="d.name"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-navigation-drawer>

      <v-card-text class="ma-0 pa-0">
        <div v-if="group === 'Sales Summary'">
          <dashboard :commatize="commatize"> ></dashboard>
        </div>
        <div v-else-if="group === 'Product Sales'">
          <product-sales
            :commatize="commatize"
            :getChartData="getChartData"
          ></product-sales>
        </div>
      </v-card-text>
    </v-card>
  </v-app>
</template>

<script>
  import ProductSales from "@/components/KPIDashboard/ProductSales.vue";
  import Dashboard from "@/components/Dashboard.vue";

  export default {
    name: "KPIDashboard",
    components: {
      ProductSales,
      Dashboard,
    },
    props: [],
    data: () => ({
      selectedItem: 0,
      dashboards: [{ id: 0, name: "Data Manager" }],
      title: "Sales Summary",
      drawer: false,
      group: "Sales Summary",
      chartCategories: {
        pie: "summary",
        donut: "summary",
        line: "phased",
        spline: "phased",
        area: "phased",
        column: "phased",
        bar: "phased",
      },
    }),
    beforeMount() {
      this.getDashboards();
    },
    methods: {
      commatize(x) {
        var sign = x < 0 ? "-" : "";
        x = Math.abs(x).toFixed(0);
        var parts = x.toString().split(".");
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        return `${sign}${parts[0]}`;
      },
      getChartData(chart) {
        var params = Object.assign(chart.sql, { type: chart.chartOptions.type });
        this.$http
          .post(`get-chart-data/`, {
            data: params,
          })
          .then((response) => {
            chart.data = response.data.data;
            chart.chartOptions.chartCategory =
              this.chartCategories[chart.chartOptions.type];
            Object.assign(chart.chartOptions, response.data.options);
          });
      },
      getDashboards() {
        this.$http.get("dashboards/", {}).then((response) => {
          response.data.forEach((d) => this.dashboards.push(d));
        });
      },
    },
    watch: {
      selectedItem(value) {
        this.drawer = false;
        if (value === "Data Manager") {
          window.open("/data-manager/", "_blank").focus();
        } else {
          this.title = value;
        }
      },
    },
  };
</script>


<style>
  .big-text {
    font-size: 18px;
  }
  .med-text {
    font-size: 16px;
  }
</style>
