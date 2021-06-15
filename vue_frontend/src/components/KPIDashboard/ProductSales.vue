<template>
  <v-app>
    <v-card>
      <v-card-title>
        <v-row>
          <v-col cols="12">
            <v-row>
              <v-col cols="4"> Sales by Product</v-col>
            </v-row>
            <!-- <v-row>
              <v-col cols="4">
                <v-combobox
                  v-model="selectedProductFamily"
                  :items="productFamilies"
                  label="Select a Product Family"
                ></v-combobox>
              </v-col>
            </v-row> -->
            <v-row>
              <v-col cols="4">
                <v-text-field
                  v-model="search"
                  append-icon="mdi-magnify"
                  label="Search Products"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-card-title>
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="productData"
          :search="search"
          :items-per-page="10"
          class="elevation-1"
          :expanded.sync="expanded"
          item-key="name"
          show-expand
          fixed-header
          multi-sort
          :loading="gridLoading"
          loading-text="Saponifying Data... Please wait"
        >
          <template v-slot:item.name="{ item }">
            <span class="med-text">{{ item.name }}</span>
          </template>
          <template v-slot:item.total_quantity="{ item }">
            <span class="big-text">{{ commatize(item.total_quantity) }}</span>
          </template>
          <template v-slot:item.average_quantity="{ item }">
            <span class="big-text">{{ commatize(item.average_quantity) }}</span>
          </template>
          <template v-slot:item.phased_quantity="{ item }">
            <chart
              :chartData="item.data"
              :options="item.options"
              :commatize="commatize"
            />
          </template>
          <template v-slot:item.total_sales="{ item }">
            <span class="big-text">${{ commatize(item.total_sales) }}</span>
          </template>
          <template v-slot:item.phased_sales="{ item }">
            <chart
              :chartData="item.data"
              :options="item.options"
              :commatize="commatize"
            />
          </template>
          <template v-slot:item.total_margin="{ item }">
            <span class="big-text">${{ commatize(item.total_margin) }}</span>
          </template>
          <template v-slot:item.phased_margin="{ item }">
            <chart
              :chartData="item.data"
              :options="item.options"
              :commatize="commatize"
            />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-app>
</template>

<script>
  import Chart from "@/components/Chart.vue";

  export default {
    name: "ProductSales",
    components: {
      Chart,
    },
    props: ["commatize", "getChartData"],
    data: function () {
      return {
        selectedProductFamily: {
          text: "All Products",
          value: "All Products",
        },
        gridLoading: true,
        productFamilies: [],
        productData: [],
        search: "",
        expanded: [],
        chart1: {},
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
            value: "total_quantity",
            sortable: true,
          },
          {
            text: "Average Quantity",
            value: "average_quantity",
          },
          {
            text: "Quantity by Month",
            value: "phased_quantity",
            sortable: false,
            align: " d-none d-lg-table-cell",
          },
          {
            text: "Total Sales",
            value: "total_sales",
            sortable: true,
          },
          {
            text: "Sales by Month",
            value: "phased_sales",
            sortable: false,
            align: " d-none d-lg-table-cell",
          },
          {
            text: "Total Margin",
            value: "total_margin",
            sortable: true,
          },
          {
            text: "Margin by Month",
            value: "phased_margin",
            sortable: false,
            align: " d-none d-lg-table-cell",
          },
        ],
      };
    },
    computed: {},
    watch: {
      selectedProductFamily: function (val) {
        this.gridLoading = true;
        this.getProductData(val.value);
      },
    },
    beforeMount() {
      // this.getPie("sales_channel");
      // this.getProductData(this.selectedProductFamily.value);
      // this.getProductFamilies();
    },
    methods: {
      getProductFamilies() {
        this.$http.get(`../product-family/`, {}).then((response) => {
          this.productFamilies = [this.selectedProductFamily].concat(
            response.data
          );
        });
      },
      getProductData(value) {
        this.$http.get(`../product-data/${value}`, {}).then((response) => {
          this.productData = response.data;
          this.gridLoading = false;
        });
      },
      // getPie(value) {
      //   this.$http
      //     .get(`../get-pie/${value}`, {
      //       // data: params
      //     })
      //     .then((response) => {
      //       this.chart1 = response.data;
      //     });
      // },
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
