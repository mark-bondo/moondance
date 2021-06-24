(function(t){function e(e){for(var a,s,o=e[0],l=e[1],c=e[2],d=0,h=[];d<o.length;d++)s=o[d],Object.prototype.hasOwnProperty.call(n,s)&&n[s]&&h.push(n[s][0]),n[s]=0;for(a in l)Object.prototype.hasOwnProperty.call(l,a)&&(t[a]=l[a]);u&&u(e);while(h.length)h.shift()();return i.push.apply(i,c||[]),r()}function r(){for(var t,e=0;e<i.length;e++){for(var r=i[e],a=!0,o=1;o<r.length;o++){var l=r[o];0!==n[l]&&(a=!1)}a&&(i.splice(e--,1),t=s(s.s=r[0]))}return t}var a={},n={"kpi-dashboard":0},i=[];function s(e){if(a[e])return a[e].exports;var r=a[e]={i:e,l:!1,exports:{}};return t[e].call(r.exports,r,r.exports,s),r.l=!0,r.exports}s.m=t,s.c=a,s.d=function(t,e,r){s.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:r})},s.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},s.t=function(t,e){if(1&e&&(t=s(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var r=Object.create(null);if(s.r(r),Object.defineProperty(r,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var a in t)s.d(r,a,function(e){return t[e]}.bind(null,a));return r},s.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return s.d(e,"a",e),e},s.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},s.p="";var o=window["webpackJsonp"]=window["webpackJsonp"]||[],l=o.push.bind(o);o.push=e,o=o.slice();for(var c=0;c<o.length;c++)e(o[c]);var u=l;i.push([0,"chunk-vendors"]),r()})({0:function(t,e,r){t.exports=r("ac66")},"02ce":function(t,e,r){},"0c57":function(t,e,r){},"2fe3":function(t,e,r){"use strict";r("02ce")},"5c8b":function(t,e,r){},ac66:function(t,e,r){"use strict";r.r(e);r("e260"),r("e6cf"),r("cca6"),r("a79d"),r("2d26"),r("96cf");var a=r("2ef0"),n=r.n(a),i=r("2b0e"),s=r("2f62"),o={state:{dashboard:{}}};i["default"].use(s["a"]);var l=new s["a"].Store({modules:{kpi:o}}),c=l,u=r("ce5b"),d=r.n(u);r("bf40");i["default"].use(d.a);var h={},p=new d.a(h),v=r("4452"),f=r.n(v),m=r("ea7f"),b=r.n(m),w=r("bc3a"),g=r.n(w),y=(r("5363"),function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("v-app",[r("v-navigation-drawer",{attrs:{absolute:"",temporary:"",app:""},model:{value:t.drawer,callback:function(e){t.drawer=e},expression:"drawer"}},[r("v-list",[r("v-subheader",[r("v-icon",[t._v("mdi-chart-bar")]),t._v("Dashboards")],1),r("v-list-item-group",{attrs:{"active-class":"deep-purple--text text--accent-4"}},[t._l(t.dashboards,(function(e){return r("v-list-item",{key:e.id,on:{click:function(r){return t.menuActionClick(e)}}},[r("v-list-item-content",[r("v-list-item-title",{domProps:{textContent:t._s(e.name)}})],1)],1)})),r("v-divider"),r("v-subheader",[r("v-icon",[t._v("mdi-tools")]),t._v("Admin")],1),t._l(t.admin,(function(e){return r("v-list-item",{key:e.id,on:{click:function(r){return t.menuActionClick(e)}}},[r("v-list-item-content",[r("v-list-item-title",{domProps:{textContent:t._s(e.name)}})],1)],1)}))],2)],1)],1),r("v-app-bar",{attrs:{color:"#302752",dark:"",app:""}},[r("v-app-bar-nav-icon",{on:{click:function(e){e.stopPropagation(),t.drawer=!t.drawer}}}),r("v-spacer"),r("v-toolbar-title",[r("h2",[t._v(t._s(t.headerTitle))])]),r("v-spacer")],1),r("v-main",[r("v-container",{attrs:{fluid:""}},[r("dashboard",{attrs:{charts:t.selectedCharts}})],1)],1)],1)}),D=[],C=(r("b680"),r("ac1f"),r("1276"),r("d3b7"),r("25f0"),r("5319"),r("99af"),r("159b"),r("b0c0"),function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("div",[r("v-row",{staticClass:"mb-3"},[r("v-tabs",{directives:[{name:"show",rawName:"v-show",value:0!==t.charts.length,expression:"charts.length !== 0"}],attrs:{centered:"","show-arrows":"","center-active":"",color:"green"},model:{value:t.dateFilter,callback:function(e){t.dateFilter=e},expression:"dateFilter"}},t._l(t.dateTabs,(function(e,a){return r("v-tab",{key:a},[t._v(t._s(e))])})),1)],1),r("v-row",t._l(t.charts,(function(e){return r("v-col",{key:e,attrs:{cols:"12",xs:"12",lg:"6"}},[r("chart",{attrs:{chartId:e,dateFilter:t.dateTabs[t.dateFilter]}})],1)})),1)],1)}),x=[],_=function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("v-card",[r("v-card-title",{staticClass:"justify-center pa-0"},[r("v-toolbar",{staticClass:"elevation-0",attrs:{dense:""}},[r("v-spacer"),r("v-toolbar-title",[t._v(t._s(t.extraOptions.title))]),r("v-spacer"),r("v-menu",{attrs:{left:"","offset-y":""},scopedSlots:t._u([{key:"activator",fn:function(e){var a=e.on,n=e.attrs;return[r("v-btn",t._g(t._b({attrs:{icon:"",dark:"",color:"#302752"}},"v-btn",n,!1),a),[r("v-icon",{attrs:{large:""}},[t._v("mdi-chart-box")])],1)]}}])},[r("v-list-item-group",{attrs:{"active-class":"deep-purple--text text--accent-4"},model:{value:t.extraOptions.selectedChartType,callback:function(e){t.$set(t.extraOptions,"selectedChartType",e)},expression:"extraOptions.selectedChartType"}},[r("v-list",t._l(t.chartMenu,(function(e){return r("v-list-item",{key:e.type,on:{click:function(r){return t.changeChartType(e)}}},[r("v-list-item-icon",[r("v-icon",{domProps:{textContent:t._s(e.icon)}})],1),r("v-list-item-content",[r("v-list-item-title",[t._v(" "+t._s(e.type))])],1)],1)})),1)],1)],1)],1)],1),r("v-card-text",[r("v-row",[r("v-col",{staticClass:"pa-0",attrs:{cols:"12"}},[r("bread-crumbs",{attrs:{AvailableDrillDowns:t.AvailableDrillDowns,selectedBreadCrumb:t.selectedBreadCrumb,drillDowns:t.drillDowns,selectedFilterValue:t.selectedFilterValue,activeIconMap:t.activeIconMap},on:{setDrillDowns:t.setDrillDowns}})],1)],1),r("v-row",[r("v-col",{attrs:{cols:"12"}},[t.isInitialLoad?t._e():r("highcharts",{attrs:{options:t.localOptions}}),r("drill-menu",{attrs:{AvailableDrillDowns:t.AvailableDrillDowns,showDrillMenu:t.showDrillMenu,chartCategory:t.extraOptions.chartCategory},on:{setParentItem:t.setParentItem}})],1),r("v-overlay",{attrs:{absolute:!0,value:t.showOverlay}},[r("v-progress-circular",{attrs:{indeterminate:"",size:70,width:7,color:"deep-purple"}})],1)],1)],1)],1)},O=[],k=r("1da1"),M=(r("4de4"),r("7db0"),function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("v-container",[r("v-breadcrumbs",{staticClass:"pa-0",attrs:{items:t.visibleBreadCrumbs},scopedSlots:t._u([{key:"item",fn:function(e){var a=e.item;return[r("v-breadcrumbs-item",[r("v-menu",{attrs:{"offset-y":"",disabled:!(!0===a.isCurrent)},scopedSlots:t._u([{key:"activator",fn:function(e){var n=e.on,i=e.attrs;return[r("v-chip",t._g(t._b({staticClass:"ma-2",attrs:{label:"","text-color":"white",color:a.icon.color,value:a.value},on:{click:function(e){return t.removeBreadCrumb(a)}}},"v-chip",i,!1),n),[null!==a.filter?r("span",[t._v(t._s(a.filter))]):r("span",[t._v(t._s(a.text))]),r("v-icon",{staticClass:"ml-1",domProps:{textContent:t._s(a.icon.current)}})],1)]}}],null,!0)},[r("v-list",t._l(t.AvailableDrillDowns,(function(e,n){return r("v-list-item",{key:e.value,attrs:{value:n,link:"",dense:""},on:{click:function(r){return t.breadCrumbMenuClick(e,a)}}},[r("v-list-item-title",[t._v(t._s(e.text))])],1)})),1)],1)],1)]}},{key:"divider",fn:function(){return[r("v-icon",[t._v("mdi-chevron-right")])]},proxy:!0}])})],1)}),j=[],B={name:"BreadCrumbs",props:["drillDowns","AvailableDrillDowns","selectedBreadCrumb","selectedFilterValue","activeIconMap"],data:function(){return{}},computed:{visibleBreadCrumbs:function(){return this.drillDowns.filter((function(t){return!0===t.isBreadCrumb}))}},watch:{selectedBreadCrumb:function(t){var e=n.a.find(this.drillDowns,{isCurrent:!0});e=Object.assign(e,{isCurrent:!1,isBreadCrumb:!0,icon:this.activeIconMap[!1],filter:this.selectedFilterValue}),Object.assign(t,{isCurrent:!0,isBreadCrumb:!0,icon:this.activeIconMap[!0],sortOrder:e.sortOrder+10}),this.$emit("setDrillDowns",n.a.orderBy(this.drillDowns,"sortOrder"))}},beforeMount:function(){},methods:{removeBreadCrumb:function(t){!0!==t.isCurrent&&(Object.assign(t,{isCurrent:!1,isBreadCrumb:!1,filter:null,icon:this.activeIconMap[!1],sortOrder:0}),this.$emit("setDrillDowns",n.a.orderBy(this.drillDowns,"sortOrder")))},breadCrumbMenuClick:function(t,e){var r=Object.assign({},t),a=Object.assign({},e);Object.assign(e,{text:r.text,value:r.value,filter:r.filter}),Object.assign(t,{text:a.text,value:a.value,filter:a.filter}),this.$emit("setDrillDowns",n.a.orderBy(this.drillDowns,"sortOrder"))}}},P=B,T=(r("f13e"),r("2877")),I=Object(T["a"])(P,M,j,!1,null,null,null),S=I.exports,$=function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("v-menu",{attrs:{"position-x":t.menu.x,"position-y":t.menu.y,"offset-y":""},model:{value:t.menu.show,callback:function(e){t.$set(t.menu,"show",e)},expression:"menu.show"}},[r("v-card",[r("v-card-text",{staticClass:"pa-1"},[r("v-list",{attrs:{dense:""}},[r("v-subheader",[t._v("Drill Down Options")]),r("v-list-item-group",{attrs:{color:"primary"}},t._l(t.AvailableDrillDowns,(function(e){return r("v-list-item",{key:e.value,on:{click:function(r){return t.drillDownSelected(e)}}},[!1===e.isBreadCrumb?r("v-list-item-content",[r("v-list-item-title",{domProps:{textContent:t._s(e.text)}})],1):t._e()],1)})),1),r("v-divider")],1)],1)],1)],1)},A=[],F={name:"DrillMenu",props:["AvailableDrillDowns","showDrillMenu","chartCategory"],data:function(){return{menu:{show:!1,x:0,y:0}}},watch:{showDrillMenu:function(t){this.menu.show=!1;var e="phased"===this.chartCategory?t.point.series.name:t.point.name;this.menu={x:t.clientX,y:t.clientY,show:!0},this.$emit("setParentItem",{name:"selectedFilterValue",value:e})}},methods:{drillDownSelected:function(t){this.$emit("setParentItem",{name:"selectedBreadCrumb",value:t})}}},E=F,V=Object(T["a"])(E,$,A,!1,null,null,null),L=V.exports,R={name:"Chart",props:["chartId","dateFilter"],components:{BreadCrumbs:S,DrillMenu:L},data:function(){return{activeIconMap:{true:{current:"mdi-eye-outline",color:"success"},false:{current:"mdi-filter-outline",color:"grey"}},showOverlay:!0,showDrillMenu:null,drillDowns:[],selectedFilterValue:null,selectedBreadCrumb:null,extraOptions:{title:"",selectedChartType:null},chartMenu:[],localOptions:{},isInitialLoad:!0}},computed:{AvailableDrillDowns:function(){return n.a.sortBy(this.drillDowns.filter((function(t){return!1===t.isBreadCrumb})),"text")}},watch:{dateFilter:function(){this.getData()}},beforeMount:function(){this.getSettings()},methods:{getSettings:function(){var t=this;return Object(k["a"])(regeneratorRuntime.mark((function e(){return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:return e.next=2,t.$http.get("default-settings/chartMenu",{});case 2:return t.chartMenu=e.sent.data,e.next=5,t.$http.get("default-settings/defaultChartOptions",{});case 5:t.localOptions=e.sent.data,t.getData();case 7:case"end":return e.stop()}}),e)})))()},changeChartType:function(t){this.selectedChartType=t.type,this.localOptions.chart.type=t.type,t.category!==this.extraOptions.chartCategory?(this.extraOptions.chartCategory=t.category,this.getData()):this.extraOptions.chartCategory=t.category},getData:function(){var t=this;this.showOverlay=!0,this.localOptions.series=[];var e=n.a.reject(this.drillDowns,{filter:null});e.push({value:this.extraOptions.xAxis,filter:this.dateFilter,type:"xaxis"}),this.$http.post("chart/".concat(this.chartId),{filters:e,grouping:n.a.find(this.drillDowns,{isCurrent:!0}),chartCategory:this.extraOptions.chartCategory}).then((function(e){var r=e.data.highCharts;t.extraOptions=e.data.extraOptions,t.isInitialLoad&&(t.drillDowns=t.extraOptions.drillDowns,t.drillDowns.forEach((function(e){return e.icon=t.activeIconMap[e.isCurrent]})),n.a.merge(t.localOptions,r),t.localOptions.series=[]),t.parseSeries(r.series),t.isInitialLoad=!1,t.showOverlay=!1}))},parseSeries:function(t){var e=this;t="phased"===this.extraOptions.chartCategory?this.parseDates(t):t,n.a.forEach(t,(function(t){e.localOptions.series.push(Object.assign(t,{point:e.createPointEvent()}))}))},createPointEvent:function(){var t=this;return{events:{click:function(e){t.showDrillMenu=e}}}},parseDates:function(t){for(var e=0;e<t.length;e++)for(var r=t[e],a=0;a<r.data.length;a++)r.data[a][0]=Date.parse(r.data[a][0]);return t},setDrillDowns:function(t){this.drillDowns=t,this.getData()},setParentItem:function(t){this[t.name]=t.value}}},N=R,H=Object(T["a"])(N,_,O,!1,null,null,null),U=H.exports,z={name:"Dashboard",components:{Chart:U},props:["charts"],data:function(){return{dateTabs:["Today","This Week","This Month","This Quarter","This Year","All Dates"],dateFilter:2}}},J=z,K=(r("2fe3"),Object(T["a"])(J,C,x,!1,null,null,null)),X=K.exports,Y={name:"KPIDashboard",components:{Dashboard:X},props:[],data:function(){return{selectedCharts:[],dashboards:[],admin:[{id:0,name:"Data Manager",type:"admin"}],headerTitle:"Home",drawer:!1}},beforeMount:function(){this.getDashboards()},methods:{commatize:function(t){var e=t<0?"-":"";t=Math.abs(t).toFixed(0);var r=t.toString().split(".");return r[0]=r[0].replace(/\B(?=(\d{3})+(?!\d))/g,","),"".concat(e).concat(r[0])},getDashboards:function(){var t=this;this.$http.get("dashboards/",{}).then((function(e){var r=t;t.$_.forEach(e.data,(function(t){r.dashboards.push(t)}))}))},menuActionClick:function(t){this.drawer=!1,"Data Manager"===t.name?window.open("/data-manager/","_blank").focus():this.headerTitle=t.name,this.selectedCharts=t.charts}}},Q=Y,W=(r("d95c"),Object(T["a"])(Q,y,D,!1,null,null,null)),Z=W.exports;function q(t,e){document.getElementById(e)&&new i["default"]({vuetify:p,Highcharts:b.a,HighchartsVue:f.a,store:c,render:function(e){return e(t)}}).$mount("#".concat(e))}b.a.setOptions({title:{text:""},lang:{decimalPoint:".",resetZoom:"Reset",thousandsSep:","},credits:!1}),g.a.defaults.xsrfCookieName="csrftoken",g.a.defaults.xsrfHeaderName="X-CSRFTOKEN",i["default"].prototype.$http=g.a.create({baseURL:Object({NODE_ENV:"production",BASE_URL:""}).VUE_APP_HOST_URL}),i["default"].prototype.$_=n.a,i["default"].use(f.a),i["default"].config.productionTip=!1,q(Z,"kpi-dashboard")},d95c:function(t,e,r){"use strict";r("5c8b")},f13e:function(t,e,r){"use strict";r("0c57")}});