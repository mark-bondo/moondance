// Polyfills - required for IE11 - must remain at top
import 'core-js/stable'
import 'regenerator-runtime/runtime';
// Imports
import _ from 'lodash'
import Vue from 'vue'
import store from "@/store"
import vuetify from '@/plugins/vuetify'
import Highcharts from 'highcharts';
import HighchartsVue from 'highcharts-vue'
import axios from 'axios'
import '@mdi/font/css/materialdesignicons.css'
import KPIDashboard from "./apps/KPIDashboard.vue"


Highcharts.setOptions({
    title: {
        text: "",
      },
    lang: {
        decimalPoint: '.',
        resetZoom: 'Reset',
        thousandsSep: ','
    },
    credits: false,
});

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

Vue.prototype.$http = axios.create({
    baseURL: process.env.VUE_APP_HOST_URL
});
Vue.prototype.$_ = _
Vue.use(HighchartsVue)
Vue.config.productionTip = false

function deployVueApp(component, id) {
  if (document.getElementById(id)) {
      new Vue({
          vuetify,
          Highcharts,
          HighchartsVue,
          store,
          render: h => h(component)
      }).$mount(`#${id}`)
  }
}

deployVueApp(KPIDashboard, 'kpi-dashboard')
