<template>
  <v-container class="pa-0">
    <v-breadcrumbs :items="visibleBreadCrumbs" class="pa-0">
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
                <span v-if="item.filter !== null">{{ item.filter }}</span>
                <span v-else>{{ item.text }}</span>

                <v-icon class="ml-1" v-text="item.icon.current"></v-icon>
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
  </v-container>
</template>
<script>
  import _ from "lodash";
  export default {
    name: "BreadCrumbs",
    props: [
      "drillDowns",
      "getData",
      "AvailableDrillDowns",
      "addedBreadCrumb",
      "selectedFilterValue",
    ],
    data: () => ({
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
    }),
    computed: {
      visibleBreadCrumbs() {
        return this.drillDowns.filter((d) => d.isBreadCrumb === true);
      },
      // sortedDrillDowns() {},
    },
    watch: {
      // drillDowns: {
      //   deep: true,
      //   handler(value) {
      //     this.$emit("updateDrillDowns", _.orderBy(value, "sortOrder"));
      //   },
      // },
      addedBreadCrumb(newItem) {
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
        this.$emit("updateDrillDowns", _.orderBy(this.drillDowns, "sortOrder"));
      },
    },
    beforeMount() {},
    methods: {
      // addBreadCrumb(newItem) {
      //   var oldItem = _.find(this.drillDowns, { isCurrent: true });
      //   oldItem = Object.assign(oldItem, {
      //     isCurrent: false,
      //     isBreadCrumb: true,
      //     icon: this.iconMap[false],
      //     filter: this.selectedFilterValue,
      //   });

      //   Object.assign(newItem, {
      //     isCurrent: true,
      //     isBreadCrumb: true,
      //     icon: this.iconMap[true],
      //     sortOrder: oldItem.sortOrder + 10,
      //   });

      //   this.drillDowns = _.orderBy(this.drillDowns, "sortOrder");
      // },
      removeBreadCrumb(removedItem) {
        if (removedItem.isCurrent !== true) {
          Object.assign(removedItem, {
            isCurrent: false,
            isBreadCrumb: false,
            filter: null,
            icon: this.iconMap[false],
            sortOrder: 0,
          });
          this.$emit("updateDrillDowns", _.orderBy(this.drillDowns, "sortOrder"));
          // this.getData();
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
        this.$emit("updateDrillDowns", _.orderBy(this.drillDowns, "sortOrder"));
        // this.getData();
      },
    },
  };
</script>

<style>
  .v-breadcrumbs li:nth-child(2n) {
    padding: 0px;
  }
</style>
