<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" absolute temporary app>
      <v-list>
        <v-subheader><v-icon>mdi-chart-bar</v-icon>Dashboards</v-subheader>
        <v-list-item-group active-class="deep-purple--text text--accent-4">
          <v-list-item
            v-for="item in dashboards"
            :key="item.id"
            @click="menuActionClick(item)"
          >
            <v-list-item-content>
              <v-list-item-title v-text="item.name"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-divider></v-divider>
          <v-subheader><v-icon>mdi-tools</v-icon>Admin</v-subheader>
          <v-list-item
            v-for="item in admin"
            :key="item.id"
            @click="menuActionClick(item)"
          >
            <v-list-item-content>
              <v-list-item-title v-text="item.name"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar color="#302752" dark app>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-spacer></v-spacer>
      <v-toolbar-title>
        <h2>{{ headerTitle }}</h2></v-toolbar-title
      >
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-main>
      <v-container fluid>
        <dashboard :charts="selectedCharts"></dashboard>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
  // import ProductSales from "@/components/KPIDashboard/ProductSales.vue";
  import Dashboard from "@/components/Dashboard.vue";
  // import _ from "lodash";

  export default {
    name: "KPIDashboard",
    components: {
      // ProductSales,
      Dashboard,
    },
    props: [],
    data: () => ({
      selectedCharts: [],
      dashboards: [],
      admin: [{ id: 0, name: "Data Manager", type: "admin" }],
      headerTitle: "Home",
      drawer: false,
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
      getDashboards() {
        this.$http.get("dashboards/", {}).then((response) => {
          var self = this;
          this.$_.forEach(response.data, function (d) {
            self.dashboards.push(d);
          });
        });
      },
      menuActionClick(item) {
        this.drawer = false;
        if (item.name === "Data Manager") {
          window.open("/data-manager/", "_blank").focus();
        } else {
          this.headerTitle = item.name;
        }

        this.selectedCharts = item.charts;
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
