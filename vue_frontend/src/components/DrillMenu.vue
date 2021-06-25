<template>
  <v-menu v-model="menu.show" :position-x="menu.x" :position-y="menu.y" offset-y
    ><v-card>
      <v-card-text class="pa-1">
        <v-list dense>
          <v-subheader>Drill Down Options</v-subheader>
          <v-list-item-group color="primary">
            <v-list-item
              v-for="item in drillItems"
              :key="item.value"
              @click="drillDownSelected(item)"
            >
              <v-list-item-content v-if="item.isBreadCrumb === false">
                <v-list-item-title v-text="item.text"></v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
          <v-divider></v-divider>
        </v-list>
      </v-card-text> </v-card
  ></v-menu>
</template>

<script>
  export default {
    name: "DrillMenu",
    props: ["drillItems", "selectedDrillItem", "chartCategory"],
    data: () => ({
      menu: {
        show: false,
        x: 0,
        y: 0,
      },
    }),
    watch: {
      selectedDrillItem(e) {
        this.menu.show = false;
        let selectedFilterValue =
          this.chartCategory === "phased" ? e.point.series.name : e.point.name;

        this.menu = {
          x: e.clientX,
          y: e.clientY,
          show: true,
        };

        this.$emit("setParentItem", {
          name: "selectedFilterValue",
          value: selectedFilterValue,
        });
      },
    },
    methods: {
      drillDownSelected(newItem) {
        this.$emit("setParentItem", {
          name: "selectedBreadCrumb",
          value: newItem,
        });
      },
    },
  };
</script>
