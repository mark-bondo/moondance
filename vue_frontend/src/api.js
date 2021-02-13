import Vue from 'vue'
import vuetify from '@/plugins/vuetify';
import axios from 'axios'
import DataTable from './DataTable.vue'
import '@mdi/font/css/materialdesignicons.css'
import HighchartsVue from 'highcharts-vue'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

Vue.prototype.$http = axios.create({
    baseURL: "http://localhost:8000/"
});

Vue.use(HighchartsVue)
Vue.config.productionTip = false

new Vue({
    axios,
    vuetify,
  render: h => h(DataTable),
}).$mount('#report-app')