// Polyfills - required for IE11 - must remain at top
import 'core-js/stable'
import 'regenerator-runtime/runtime';
// Imports
import Vue from 'vue'
import vuetify from '@/plugins/vuetify'
import HighchartsVue from 'highcharts-vue'
import Highcharts from 'highcharts';
import axios from 'axios'
import _ from 'lodash'
import '@mdi/font/css/materialdesignicons.css'

import KPIDashboard from "./apps/KPIDashboard.vue"

Highcharts.setOptions({
    lang: {
        decimalPoint: '.',
        resetZoom: 'Reset',
        thousandsSep: ','
    }
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
          render: h => h(component)
      }).$mount(`#${id}`)
  }
}

deployVueApp(KPIDashboard, 'kpi-dashboard')
