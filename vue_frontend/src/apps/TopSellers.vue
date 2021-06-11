<template>
  <v-app>
    <v-card class="ma-5">
      <v-card-title>Sales Dashboard</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="4">
            <v-combobox
              v-model="selectedProductFamily"
              :items="productFamilies"
              label="Select a Product Family"
              class="mx-5"
            ></v-combobox>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <!-- <v-card>
              <v-container> -->
            <!-- <v-row class="v-card__title">
                  <v-col cols="6"> Title </v-col>
                  <v-spacer />
                </v-row> -->
            <v-data-table
              :headers="headers"
              :items="productData"
              :search="search"
              :items-per-page="10"
              class="elevation-1"
              :expanded.sync="expanded"
              item-key="name"
              show-expand
            >
              <template v-slot:item.total_quantity="{ item }">
                {{ commatize(item.total_quantity) }}
              </template>
              <template v-slot:item.phased_quantity="{ item }">
                <line-chart
                  :name="item.name"
                  type="quantity"
                  :chartData="item.phased_quantity"
                  :xaxis="item.xaxis"
                />
              </template>
              <template v-slot:item.total_sales="{ item }">
                ${{ commatize(item.total_sales) }}
              </template>
              <template v-slot:item.phased_sales="{ item }">
                <line-chart
                  :name="item.name"
                  type="sales"
                  :chartData="item.phased_sales"
                  :xaxis="item.xaxis"
                />
              </template>
              <template v-slot:item.total_margin="{ item }">
                ${{ commatize(item.total_margin) }}
              </template>
              <template v-slot:item.phased_margin="{ item }">
                <line-chart
                  :name="item.name"
                  type="margin"
                  :chartData="item.phased_margin"
                  :xaxis="item.xaxis"
                />
              </template>
            </v-data-table>
            <!-- </v-container>
            </v-card> -->
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-app>
</template>

<script>
  import LineChart from "@/components/LineChart.vue";

  export default {
    name: "TopSellers",
    components: {
      LineChart,
    },
    props: [],
    data: function () {
      return {
        selectedProductFamily: {
          text: null,
          value: null,
        },
        productFamilies: [],
        productData: [],
        search: "",
        expanded: [],
        headers: [
          { text: "", value: "data-table-expand" },
          {
            text: "Name",
            sortable: true,
            filterable: true,
            value: "name",
          },
          {
            text: "Total Quantity",
            sortable: true,
            filterable: true,
            value: "total_quantity",
          },
          {
            text: "Quantity by Month",
            sortable: true,
            filterable: true,
            value: "phased_quantity",
          },
          {
            text: "Total Sales",
            sortable: true,
            filterable: true,
            value: "total_sales",
          },
          {
            text: "Sales by Month",
            sortable: true,
            filterable: true,
            value: "phased_sales",
          },
          // {
          //   text: "Total Cost",
          //   sortable: true,
          //   filterable: true,
          //   value: "total_cost",
          // },
          // {
          //   text: "Cost by Month",
          //   sortable: true,
          //   filterable: true,
          //   value: "phased_cost",
          // },
          {
            text: "Total Margin",
            sortable: true,
            filterable: true,
            value: "total_margin",
          },
          {
            text: "Margin by Month",
            sortable: true,
            filterable: true,
            value: "phased_margin",
          },
        ],
      };
    },
    computed: {},
    watch: {
      selectedProductFamily: function (val) {
        this.getProductData(val.value);
      },
    },
    beforeMount() {
      this.$http
        .get(`../product-family/`, {
          // data: params
        })
        .then((response) => {
          this.productFamilies = response.data;
        });
    },
    methods: {
      // parseDates(series) {
      //   for (let i = 0; i < series.length; i++) {
      //     var obj = series[i];

      //     for (let x = 0; x < obj.data.length; x++) {
      //       obj.data[x][0] = Date.parse(obj.data[x][0]);
      //     }
      //   }
      //   return series;
      // },
      getProductData(value) {
        this.$http
          .get(`../product-data/${value}`, {
            // data: params
          })
          .then((response) => {
            this.productData = response.data;
          });
      },
      commatize(x) {
        var sign = x < 0 ? "-" : "";
        x = Math.abs(x).toFixed(0);
        var parts = x.toString().split(".");
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        return `${sign}${parts[0]}`;
      },
    },
  };
</script>
