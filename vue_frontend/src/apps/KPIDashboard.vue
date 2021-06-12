<template>
  <v-app>
    <v-card class="overflow-hidden">
      <v-app-bar color="deep-purple darken-3" dark>
        <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>

        <v-spacer></v-spacer>

        <v-toolbar-title><h2>MoonDance Soaps Dashboard</h2></v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn icon>
          <v-icon>mdi-magnify</v-icon>
        </v-btn>
        <v-btn icon>
          <v-icon>mdi-filter</v-icon>
        </v-btn>
      </v-app-bar>

      <v-navigation-drawer v-model="drawer" absolute bottom temporary>
        <v-list nav dense>
          <v-list-item-group
            v-model="group"
            active-class="deep-purple--text text--accent-4"
          >
            <v-list-item>
              <v-list-item-title>Product Sales</v-list-item-title>
            </v-list-item>

            <v-list-item @click="openDataManager">
              <v-list-item-title>Data Manager</v-list-item-title>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </v-navigation-drawer>

      <v-card-text class="ma-0 pa-0">
        <product-sales></product-sales>
      </v-card-text>
    </v-card>
  </v-app>
</template>

<script>
  import ProductSales from "@/components/KPIDashboard/ProductSales.vue";

  export default {
    name: "KPIDashboard",
    components: {
      ProductSales,
    },
    props: [],
    data: () => ({
      drawer: false,
      group: null,
    }),
    methods: {
      openDataManager() {
        window.open("/data-manager/", "_blank").focus();
      },
    },
    watch: {
      group() {
        this.drawer = false;
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
