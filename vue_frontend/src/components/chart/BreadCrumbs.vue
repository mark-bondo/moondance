<template>
  <v-container>
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
                v-for="(i, index) in drillItems"
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
      "fields",
      "drillItems",
      "selectedBreadCrumb",
      "selectedFilterValue",
      "activeIconMap",
    ],
    data: () => ({}),
    computed: {
      visibleBreadCrumbs() {
        return _.filter(this.fields, { isBreadCrumb: true, type: "grouping" });
      },
    },
    watch: {
      selectedBreadCrumb(newItem) {
        var oldItem = _.find(this.fields, { isCurrent: true, type: "grouping" });
        oldItem = Object.assign(oldItem, {
          isCurrent: false,
          isBreadCrumb: true,
          icon: this.activeIconMap[false],
          filter: this.selectedFilterValue,
        });

        Object.assign(newItem, {
          isCurrent: true,
          isBreadCrumb: true,
          icon: this.activeIconMap[true],
          sort: oldItem.sort + 10,
        });
        this.$emit("setFields", _.orderBy(this.fields, "sort"));
      },
    },
    beforeMount() {},
    methods: {
      removeBreadCrumb(removedItem) {
        if (removedItem.isCurrent !== true) {
          Object.assign(removedItem, {
            isCurrent: false,
            isBreadCrumb: false,
            filter: null,
            icon: this.activeIconMap[false],
            sort: 0,
          });
          this.$emit("setFields", _.orderBy(this.fields, "sort"));
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
        this.$emit("setFields", _.orderBy(this.fields, "sort"));
      },
    },
  };
</script>

<style>
  .v-breadcrumbs li:nth-child(2n) {
    padding: 0px;
  }
</style>
