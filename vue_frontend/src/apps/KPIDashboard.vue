<template>
  <v-app>
    <v-card height="100%">
      <v-app-bar
        color="#302752"
        dark
        hide-on-scroll
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
          ><h2>{{ headerTitle }}</h2></v-toolbar-title
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
          <v-subheader
            ><v-icon class="pr-3">mdi-chart-bar</v-icon>Dashboards</v-subheader
          >
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
            <v-subheader
              ><v-icon class="pr-3">mdi-tools</v-icon>Admin</v-subheader
            >
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

      <v-card-text class="ma-0 pa-0">
        <div v-if="selectedItem.type === 'dashboard'">
          <dashboard :dashboardId="selectedItem.id"></dashboard>
        </div>
        <div v-else-if="selectedItem === 'Product Sales'">
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
  import _ from "lodash";

  export default {
    name: "KPIDashboard",
    components: {
      ProductSales,
      Dashboard,
    },
    props: [],
    data: () => ({
      selectedItem: {},
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
          _.forEach(response.data, function (d) {
            self.dashboards.push(d);
            self.$store.state.kpi.dashboard[d.id] = d;
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

        this.selectedItem = item;
      },
    },
    watch: {},
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
