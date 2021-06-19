import Vue from "vue"
import Vuex from "vuex"

// vuex modules
import kpi from "./modules/kpi"

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    kpi,
  },
})

export default store
