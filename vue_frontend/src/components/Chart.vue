<template>
  <v-container>
    <v-card>
      <v-card-title class="justify-center">{{
        extraOptions.title
      }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" class="pa-0">
            <v-breadcrumbs :items="VisibleBreadCrumbs" class="pa-0">
              <template v-slot:item="{ item }">
                <v-breadcrumbs-item>
                  <v-chip
                    class="ma-2"
                    text-color="white"
                    :color="item.icon.color"
                    :value="item.value"
                    @mouseover="item.icon.current = item.icon.remove"
                    @mouseleave="item.icon.current = item.icon.add"
                    @click="removeBreadCrumb(item)"
                  >
                    {{ item.breadCrumbText }}
                    <v-icon class="ml-1" v-text="item.icon.current"></v-icon>
                  </v-chip>
                </v-breadcrumbs-item>
              </template>
              <template v-slot:divider>
                <v-icon>mdi-chevron-right</v-icon>
              </template>
            </v-breadcrumbs>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12" class="pa-0">
            <highcharts
              ref="chartComponent"
              class="chart"
              :options="localOptions"
            ></highcharts>
            <v-menu
              v-model="menu.show"
              :position-x="menu.x"
              :position-y="menu.y"
              offset-y
              ><v-card>
                <v-card-text>
                  <v-list dense>
                    <v-subheader>Drill Down</v-subheader>
                    <v-list-item-group color="primary">
                      <v-list-item
                        v-for="item in AvailableDrillDowns"
                        :key="item.value"
                        @click="getDrillDown(item)"
                      >
                        <v-list-item-content v-if="item.isBreadCrumb === false">
                          <v-list-item-title
                            v-text="item.text"
                          ></v-list-item-title>
                        </v-list-item-content>
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text> </v-card
            ></v-menu>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
  import _ from "lodash";
  export default {
    name: "Chart",
    props: ["chartId", "commatize"],
    data: () => ({
      menu: {
        show: false,
        x: 0,
        y: 0,
      },
      breadCrumbs: [],
      iconMap: {
        true: {
          current: "mdi-eye-outline",
          add: "mdi-eye-outline",
          remove: "mdi-close-circle-outline",
          color: "green",
        },
        false: {
          current: "mdi-filter-outline",
          add: "mdi-filter-outline",
          remove: "mdi-close-circle-outline",
          color: "grey",
        },
      },
      drillDowns: [
        {
          text: "Product Family",
          value: "product_family",
          filter: null,
          breadCrumbText: "Product Family",
          isCurrent: true,
          isBreadCrumb: true,
          sortOrder: 1,
        },
        {
          text: "Product Category",
          value: "product_category",
          filter: null,
          breadCrumbText: "Product Category",
          isCurrent: false,
          isBreadCrumb: false,
          sortOrder: -1,
        },
        {
          text: "Customer Type",
          value: "customer_type",
          filter: null,
          breadCrumbText: "Customer Type",
          isCurrent: false,
          isBreadCrumb: false,
          sortOrder: -1,
        },
      ],
      selectedFilterValue: null,
      filters: [],
      chartMap: {
        pie: "summary",
        donut: "summary",
        area: "phased",
        line: "phased",
        spline: "phased",
        column: "phased",
        bar: "phased",
      },
      extraOptions: {
        grouping: { value: null },
        title: "Loading Chart",
      },
      localOptions: {
        title: {
          text: "",
        },
        credits: false,
        chart: {
          backgroundColor: "transparent",
          style: {
            overflow: "visible",
          },
        },
        tooltip: {
          hideDelay: 0,
          outside: true,
          shared: true,
          pointFormat: "<b>{point.y}</b><br/>",
        },
        legend: {
          enabled: true,
        },
        xAxis: {
          dateTimeLabelFormats: {
            month: "%b %Y",
            year: "%Y",
          },
        },
        series: [],
      },
    }),
    computed: {
      AvailableDrillDowns() {
        return this.drillDowns.filter((d) => d.isBreadCrumb === false);
      },
      VisibleBreadCrumbs() {
        return this.drillDowns.filter((d) => d.isBreadCrumb === true);
      },
    },
    beforeMount() {
      this.drillDowns.forEach((d) => (d.icon = this.iconMap[d.isCurrent]));

      this.getData();
    },
    mounted() {},
    methods: {
      getData() {
        this.localOptions.series = [];
        var filters = [];

        this.drillDowns.forEach(function (d) {
          if (d.filter !== null) {
            filters.push({ filter: d.filter, value: d.value });
          }
        });

        this.$http
          .post(`chart/${this.chartId}`, {
            data: Object.assign(
              {
                filters: filters,
              },
              {
                grouping: this.drillDowns.filter((d) => d.isCurrent === true)[0]
                  .value,
              }
            ),
          })
          .then((response) => {
            let serverOptions = response.data.highCharts;
            this.extraOptions = response.data.extraOptions;

            if (this.extraOptions.category === "phased") {
              serverOptions.series = this.parseDates(serverOptions.series);
            }

            serverOptions.series.forEach(
              (s) => (s.point = this.createPointEvent())
            );

            this.localOptions = _.merge(this.localOptions, serverOptions);
            this.localOptions.series = [];
            serverOptions.series.forEach((s) => this.localOptions.series.push(s));
          });
      },
      createPointEvent() {
        return {
          events: {
            click: (e) => {
              this.showDrillMenu(e);
            },
          },
        };
      },
      parseDates(series) {
        for (let i = 0; i < series.length; i++) {
          var obj = series[i];

          for (let x = 0; x < obj.data.length; x++) {
            obj.data[x][0] = Date.parse(obj.data[x][0]);
          }
        }
        return series;
      },
      showDrillMenu(e) {
        this.menu.show = false;

        if (this.extraOptions.category === "phased") {
          this.selectedFilterValue = e.point.series.name;
        } else {
          this.selectedFilterValue = e.point.name;
        }

        this.menu = {
          x: e.clientX,
          y: e.clientY,
          show: true,
        };
      },
      getDrillDown(newItem) {
        this.extraOptions.grouping = newItem;

        var oldItem = this.drillDowns[_.findIndex(this.drillDowns, "isCurrent")];
        oldItem = Object.assign(oldItem, {
          isCurrent: false,
          isBreadCrumb: true,
          icon: this.iconMap[false],
          filter: this.selectedFilterValue,
          breadCrumbText: this.selectedFilterValue,
        });

        newItem = Object.assign(newItem, {
          isCurrent: true,
          isBreadCrumb: true,
          icon: this.iconMap[true],
          breadCrumbText: newItem.text,
          sortOrder: oldItem.sortOrder + 1,
        });

        this.getData();
      },
      removeBreadCrumb(removedItem) {
        if (removedItem.isCurrent === true) {
          var index = _.findIndex(this.drillDowns, { isCurrent: true });

          var newItem = this.drillDowns[index - 1];
          Object.assign(newItem, {
            isCurrent: true,
            breadCrumbText: newItem.text,
            icon: this.iconMap[true],
          });
        }

        console.log(this.drillDowns[index - 1]);

        Object.assign(removedItem, {
          isCurrent: false,
          isBreadCrumb: false,
          filter: null,
          icon: this.iconMap[false],
          sortOrder: -1,
        });

        // console.log(removedItem);
        this.getData();
      },
    },
  };
</script>

<style>
  .v-breadcrumbs li:nth-child(2n) {
    padding: 0px;
  }
</style>
