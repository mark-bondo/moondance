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
                  <v-menu offset-y :disabled="!(item.isCurrent === true)">
                    <template v-slot:activator="{ on, attrs }">
                      <v-chip
                        class="ma-2"
                        label
                        text-color="white"
                        :color="item.icon.color"
                        :value="item.value"
                        @click="removeBreadCrumb(item)"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <span v-if="item.filter !== null">{{
                          item.filter
                        }}</span>
                        <span v-else>{{ item.text }}</span>

                        <v-icon
                          class="ml-1"
                          v-text="item.icon.current"
                        ></v-icon>
                      </v-chip>
                    </template>
                    <v-list>
                      <v-list-item
                        v-for="(i, index) in AvailableDrillDowns"
                        :key="i.value"
                        :value="index"
                        @click="breadCrumbMenuClick(i, item)"
                        link
                        dense
                      >
                        <v-list-item-title>{{ i.text }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
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
                        @click="drillDownSelected(item)"
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
      iconMap: {
        true: {
          current: "mdi-eye-outline",
          color: "green",
        },
        false: {
          current: "mdi-filter-outline",
          color: "grey",
        },
      },
      drillDowns: [],
      selectedFilterValue: null,
      extraOptions: {
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
          shared: false,
          valueDecimals: 0,
          pointFormat: "{series.name}: <b>{point.y}</b><br/>",
        },
        plotOptions: {
          pie: {
            dataLabels: {
              enabled: true,
              format:
                "<b>{point.name}</b><br>{point.y:,.0f} ({point.percentage:.1f}%)",
            },
          },
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
      this.getData();
    },
    methods: {
      getData() {
        this.localOptions.series = [];
        this.$http
          .post(`chart/${this.chartId}`, {
            filters: _.reject(this.drillDowns, { filter: null }),
            grouping: _.find(this.drillDowns, { isCurrent: true }),
          })
          .then((response) => {
            let serverOptions = response.data.highCharts;
            this.extraOptions = response.data.extraOptions;

            if (this.drillDowns.length === 0) {
              this.drillDowns = this.extraOptions.drillDowns;
              this.drillDowns.forEach(
                (d) => (d.icon = this.iconMap[d.isCurrent])
              );
            }

            if (this.extraOptions.category === "phased") {
              serverOptions.series = this.parseDates(serverOptions.series);
            }

            serverOptions.series.forEach(
              (s) => (s.point = this.createPointEvent())
            );

            _.merge(this.localOptions, serverOptions);
            this.localOptions.series = [];
            this.localOptions.plotOptions = Object.assign(
              {},
              this.localOptions.plotOptions
            );
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

        this.selectedFilterValue =
          this.extraOptions.category === "phased"
            ? e.point.series.name
            : (this.selectedFilterValue = e.point.name);

        this.menu = {
          x: e.clientX,
          y: e.clientY,
          show: true,
        };
      },
      drillDownSelected(newItem) {
        this.extraOptions.grouping = newItem;
        this.addBreadCrumb(newItem);
        this.getData();
      },
      addBreadCrumb(newItem) {
        var oldItem = _.find(this.drillDowns, { isCurrent: true });
        oldItem = Object.assign(oldItem, {
          isCurrent: false,
          isBreadCrumb: true,
          icon: this.iconMap[false],
          filter: this.selectedFilterValue,
        });

        Object.assign(newItem, {
          isCurrent: true,
          isBreadCrumb: true,
          icon: this.iconMap[true],
          sortOrder: oldItem.sortOrder + 10,
        });

        this.drillDowns = _.orderBy(this.drillDowns, "sortOrder");
      },
      removeBreadCrumb(removedItem) {
        if (removedItem.isCurrent !== true) {
          Object.assign(removedItem, {
            isCurrent: false,
            isBreadCrumb: false,
            filter: null,
            icon: this.iconMap[false],
            sortOrder: 0,
          });
          this.getData();
        }
      },
      breadCrumbMenuClick(newItem, oldItem) {
        let newItemCopy = Object.assign({}, newItem);
        let oldItemCopy = Object.assign({}, oldItem);

        Object.assign(oldItem, {
          text: newItemCopy.text,
          value: newItemCopy.value,
          filter: newItemCopy.filter,
        });
        Object.assign(newItem, {
          text: oldItemCopy.text,
          value: oldItemCopy.value,
          filter: oldItemCopy.filter,
        });

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
