(function(t){function e(e){for(var n,s,i=e[0],c=e[1],l=e[2],p=0,d=[];p<i.length;p++)s=i[p],Object.prototype.hasOwnProperty.call(r,s)&&r[s]&&d.push(r[s][0]),r[s]=0;for(n in c)Object.prototype.hasOwnProperty.call(c,n)&&(t[n]=c[n]);u&&u(e);while(d.length)d.shift()();return o.push.apply(o,l||[]),a()}function a(){for(var t,e=0;e<o.length;e++){for(var a=o[e],n=!0,i=1;i<a.length;i++){var c=a[i];0!==r[c]&&(n=!1)}n&&(o.splice(e--,1),t=s(s.s=a[0]))}return t}var n={},r={"top-sellers":0},o=[];function s(e){if(n[e])return n[e].exports;var a=n[e]={i:e,l:!1,exports:{}};return t[e].call(a.exports,a,a.exports,s),a.l=!0,a.exports}s.m=t,s.c=n,s.d=function(t,e,a){s.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:a})},s.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},s.t=function(t,e){if(1&e&&(t=s(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var a=Object.create(null);if(s.r(a),Object.defineProperty(a,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var n in t)s.d(a,n,function(e){return t[e]}.bind(null,n));return a},s.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return s.d(e,"a",e),e},s.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},s.p="";var i=window["webpackJsonp"]=window["webpackJsonp"]||[],c=i.push.bind(i);i.push=e,i=i.slice();for(var l=0;l<i.length;l++)e(i[l]);var u=c;o.push([0,"chunk-vendors"]),a()})({0:function(t,e,a){t.exports=a("ac66")},"104f":function(t,e,a){"use strict";a("71f6")},"71f6":function(t,e,a){},ac66:function(t,e,a){"use strict";a.r(e);a("e260"),a("e6cf"),a("cca6"),a("a79d"),a("2d26"),a("96cf");var n=a("2b0e"),r=a("ce5b"),o=a.n(r);a("bf40");n["default"].use(o.a);var s={},i=new o.a(s),c=a("4452"),l=a.n(c),u=a("ea7f"),p=a.n(u),d=a("bc3a"),h=a.n(d),f=a("2ef0"),m=a.n(f),v=(a("5363"),function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-app",[a("v-card",[a("v-card-title",[a("v-row",[a("v-col",{attrs:{cols:"4"}},[t._v(" Sales Summary")])],1)],1),a("v-card-text",[a("v-row",[a("v-col",{attrs:{cols:"4"}},[a("pie-chart",{attrs:{name:"Sales by Sales Channel",type:"sales",chartData:t.chart1}})],1),a("v-col",{attrs:{cols:"4"}}),a("v-col",{attrs:{cols:"4"}})],1)],1)],1),a("v-card",[a("v-card-title",[a("v-row",[a("v-col",{attrs:{cols:"12"}},[a("v-row",[a("v-col",{attrs:{cols:"4"}},[t._v(" Sales by Product")])],1),a("v-row",[a("v-col",{attrs:{cols:"4"}},[a("v-text-field",{attrs:{"append-icon":"mdi-magnify",label:"Search Products"},model:{value:t.search,callback:function(e){t.search=e},expression:"search"}})],1)],1)],1)],1)],1),a("v-card-text",[a("v-data-table",{staticClass:"elevation-1",attrs:{headers:t.headers,items:t.productData,search:t.search,"items-per-page":10,expanded:t.expanded,"item-key":"name","show-expand":"",loading:t.gridLoading,"loading-text":"Saponifying Data... Please wait"},on:{"update:expanded":function(e){t.expanded=e}},scopedSlots:t._u([{key:"item.name",fn:function(e){var n=e.item;return[a("span",{staticClass:"med-text"},[t._v(t._s(n.name))])]}},{key:"item.total_quantity",fn:function(e){var n=e.item;return[a("span",{staticClass:"big-text"},[t._v(t._s(t.commatize(n.total_quantity)))])]}},{key:"item.average_quantity",fn:function(e){var n=e.item;return[a("span",{staticClass:"big-text"},[t._v(t._s(t.commatize(n.average_quantity)))])]}},{key:"item.phased_quantity",fn:function(t){var e=t.item;return[a("spark-line-chart",{attrs:{name:e.name,type:"quantity",chartData:e.phased_quantity,xaxis:e.xaxis}})]}},{key:"item.total_sales",fn:function(e){var n=e.item;return[a("span",{staticClass:"big-text"},[t._v("$"+t._s(t.commatize(n.total_sales)))])]}},{key:"item.phased_sales",fn:function(t){var e=t.item;return[a("spark-line-chart",{attrs:{name:e.name,type:"sales",chartData:e.phased_sales,xaxis:e.xaxis}})]}},{key:"item.total_margin",fn:function(e){var n=e.item;return[a("span",{staticClass:"big-text"},[t._v("$"+t._s(t.commatize(n.total_margin)))])]}},{key:"item.phased_margin",fn:function(t){var e=t.item;return[a("spark-line-chart",{attrs:{name:e.name,type:"margin",chartData:e.phased_margin,xaxis:e.xaxis}})]}}])})],1)],1)],1)}),y=[],g=(a("99af"),a("b680"),a("d3b7"),a("ac1f"),a("25f0"),a("5319"),a("1276"),function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-container",[a("highcharts",{staticClass:"chart",attrs:{options:t.chartOptions}})],1)}),b=[],x=(a("b0c0"),{name:"SparkLineChart",props:["name","type","chartData","xaxis"],data:function(){return{chartOptions:{},series:{quantity:{color:"#0c5ea2",format:""},sales:{color:"#88075f",format:"$"},margin:{color:"#019c15",format:""}}}},beforeMount:function(){this.chartOptions={title:{text:""},credits:!1,chart:{width:160,height:65,type:"area",margin:[0,0,4,0],backgroundColor:"transparent",style:{overflow:"visible"}},xAxis:{categories:this.xaxis},legend:{enabled:!1},tooltip:{hideDelay:0,outside:!0,shared:!0,valueDecimals:0,pointFormat:"<span>".concat(this.name,"</span>: <b>\n              ").concat(this.series[this.type].format,"\n              {point.y}<br/>\n              ")},series:[{name:this.type,data:this.chartData,color:this.series[this.type].color}]}},watch:{},methods:{}}),_=x,P=a("2877"),O=Object(P["a"])(_,g,b,!1,null,null,null),w=O.exports,k=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("v-container",[a("highcharts",{staticClass:"chart",attrs:{options:t.chartOptions}})],1)},S=[],D={name:"PieChart",props:["name","type","chartData"],data:function(){return{chartOptions:{},series:{quantity:{color:"#0c5ea2",format:""},sales:{color:"#88075f",format:"$"},margin:{color:"#019c15",format:""}}}},beforeMount:function(){this.chartOptions={title:{text:""},credits:!1,chart:{type:"pie",backgroundColor:"transparent"},tooltip:{hideDelay:0,outside:!0,shared:!0,valueDecimals:0,pointFormat:"<span>".concat(this.name,"</span>: <b>\n                      ").concat(this.series[this.type].format,"\n                      {point.y}<br/>\n                      ")},series:[]}},watch:{chartData:function(t){console.log(t),this.chartOptions.series={name:this.name,data:t}}},methods:{}},C=D,j=Object(P["a"])(C,k,S,!1,null,null,null),M=j.exports,$={name:"TopSellers",components:{SparkLineChart:w,PieChart:M},props:[],data:function(){return{selectedProductFamily:{text:"All Products",value:"All Products"},gridLoading:!0,productFamilies:[],productData:[],search:"",expanded:[],chart1:{},headers:[{text:"",value:"data-table-expand"},{text:"Name",sortable:!0,filterable:!0,value:"name"},{text:"Total Quantity",value:"total_quantity",sortable:!0},{text:"Average Quantity",value:"average_quantity"},{text:"Quantity by Month",value:"phased_quantity",sortable:!1},{text:"Total Sales",value:"total_sales",sortable:!0},{text:"Sales by Month",value:"phased_sales",sortable:!1},{text:"Total Margin",value:"total_margin",sortable:!0},{text:"Margin by Month",value:"phased_margin",sortable:!1}]}},computed:{},watch:{selectedProductFamily:function(t){this.gridLoading=!0,this.getProductData(t.value)}},beforeMount:function(){this.getPie("sales_channel"),this.getProductData(this.selectedProductFamily.value),this.getProductFamilies()},methods:{getProductFamilies:function(){var t=this;this.$http.get("../product-family/",{}).then((function(e){t.productFamilies=[t.selectedProductFamily].concat(e.data)}))},getProductData:function(t){var e=this;this.$http.get("../product-data/".concat(t),{}).then((function(t){e.productData=t.data,e.gridLoading=!1}))},getPie:function(t){var e=this;this.$http.get("../get-pie/".concat(t),{}).then((function(t){e.chart1=t.data}))},commatize:function(t){var e=t<0?"-":"";t=Math.abs(t).toFixed(0);var a=t.toString().split(".");return a[0]=a[0].replace(/\B(?=(\d{3})+(?!\d))/g,","),"".concat(e).concat(a[0])}}},q=$,F=(a("104f"),Object(P["a"])(q,v,y,!1,null,null,null)),E=F.exports;function L(t,e){document.getElementById(e)&&new n["default"]({vuetify:i,Highcharts:p.a,HighchartsVue:l.a,render:function(e){return e(t)}}).$mount("#".concat(e))}h.a.defaults.xsrfCookieName="csrftoken",h.a.defaults.xsrfHeaderName="X-CSRFTOKEN",n["default"].prototype.$http=h.a.create({baseURL:Object({NODE_ENV:"production",BASE_URL:""}).VUE_APP_HOST_URL}),n["default"].prototype.$_=m.a,n["default"].use(l.a),n["default"].config.productionTip=!1,L(E,"top-sellers")}});