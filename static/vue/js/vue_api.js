(function(e){function t(t){for(var n,r,l=t[0],s=t[1],u=t[2],p=0,d=[];p<l.length;p++)r=l[p],Object.prototype.hasOwnProperty.call(o,r)&&o[r]&&d.push(o[r][0]),o[r]=0;for(n in s)Object.prototype.hasOwnProperty.call(s,n)&&(e[n]=s[n]);c&&c(t);while(d.length)d.shift()();return a.push.apply(a,u||[]),i()}function i(){for(var e,t=0;t<a.length;t++){for(var i=a[t],n=!0,l=1;l<i.length;l++){var s=i[l];0!==o[s]&&(n=!1)}n&&(a.splice(t--,1),e=r(r.s=i[0]))}return e}var n={},o={vue_api:0},a=[];function r(t){if(n[t])return n[t].exports;var i=n[t]={i:t,l:!1,exports:{}};return e[t].call(i.exports,i,i.exports,r),i.l=!0,i.exports}r.m=e,r.c=n,r.d=function(e,t,i){r.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:i})},r.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},r.t=function(e,t){if(1&t&&(e=r(e)),8&t)return e;if(4&t&&"object"===typeof e&&e&&e.__esModule)return e;var i=Object.create(null);if(r.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var n in e)r.d(i,n,function(t){return e[t]}.bind(null,n));return i},r.n=function(e){var t=e&&e.__esModule?function(){return e["default"]}:function(){return e};return r.d(t,"a",t),t},r.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},r.p="";var l=window["webpackJsonp"]=window["webpackJsonp"]||[],s=l.push.bind(l);l.push=t,l=l.slice();for(var u=0;u<l.length;u++)t(l[u]);var c=s;a.push([0,"chunk-vendors"]),i()})({0:function(e,t,i){e.exports=i("d722")},d722:function(e,t,i){"use strict";i.r(t);i("e260"),i("e6cf"),i("cca6"),i("a79d");var n=i("2b0e"),o=i("ce5b"),a=i.n(o);i("bf40");n["default"].use(a.a);var r={},l=new a.a(r),s=i("bc3a"),u=i.n(s),c=function(){var e=this,t=e.$createElement,i=e._self._c||t;return i("v-card",{staticClass:"ma-5"},[i("v-card-title",[e._v("API Report Demo")]),i("v-card-text",[i("v-row",[i("v-col",{attrs:{cols:"4"}},[i("v-combobox",{staticClass:"mx-5",attrs:{items:e.apiList,label:"Select an API"},model:{value:e.api,callback:function(t){e.api=t},expression:"api"}})],1)],1),i("v-row",[i("v-col",{attrs:{cols:"12"}},[i("div",{attrs:{id:"contentSection"}},[i("ag-grid-vue",{staticClass:"ag-theme-alpine",staticStyle:{width:"100%",height:"350px"},attrs:{gridOptions:e.gridOptions,columnDefs:e.columnDefs,defaultColDef:e.defaultColDef,rowData:e.rowData,cacheBlockSize:e.cacheBlockSize,rowModelType:e.rowModelType,serverSideStoreType:e.serverSideStoreType,modules:e.modules},on:{"grid-ready":e.onGridReady}})],1),i("div",{staticClass:"text-center mt-3 display"},[i("v-pagination",{attrs:{length:e.page.count,"total-visible":7,"prev-icon":"mdi-menu-left","next-icon":"mdi-menu-right"},model:{value:e.page.selected,callback:function(t){e.$set(e.page,"selected",t)},expression:"page.selected"}}),i("div",[e._v(" records found: "+e._s(e.rowCount)+" ")])],1)])],1)],1)],1)},p=[],d=i("401b"),f=(i("599e"),i("71db")),g={name:"dataTable",components:{AgGridVue:d["AgGridVue"]},props:[],data:function(){return{rowCount:null,page:{selected:1,url:null,count:0},apiList:[],api:{text:null,value:null},modules:[f["a"]],rowModelType:"serverSide",serverSideStoreType:"partial",cacheBlockSize:50,columnDefs:null,rowData:null,gridOptions:{pagination:!0,paginationPageSize:50,suppressPaginationPanel:!0},defaultColDef:{flex:1,minWidth:110,sortable:!0,resizable:!0,floatingFilter:!0,menuTabs:["filterMenuTab","generalMenuTab"]}}},computed:{},watch:{api:function(){this.rowCount=null,this.onGridReady()},"page.selected":function(e){console.log(e),this.gridApi.paginationGoToPage(e-1)},rowCount:function(e){this.page.count=Math.ceil(e/this.gridOptions.paginationPageSize)}},mounted:function(){this.gridApi=this.gridOptions.api,this.gridColumnApi=this.gridOptions.columnApi,this.getApiList()},methods:{onGridReady:function(){var e=this,t=this.api.value;if(t){var i={getRows:function(i){e.$http.post("/api/2021-01/".concat(t,"/get/"),{data:i.request,headers:{"Content-Type":"application/json; charset=utf-8"}}).then((function(t){var n=t.data.rowData.length;i.successCallback(t.data.rowData,e.rowCount),e.columnDefs=t.data.columnDefs,e.getRowCount(n)}))}};this.gridOptions.api.setServerSideDatasource(i)}},getRowCount:function(e){var t=this,i=this.api.value+JSON.stringify(this.gridApi.getFilterModel());if(i!==this.page.url)if(e<50)this.rowCount=e;else{this.rowCount=null;var n={filterModel:this.gridApi.getFilterModel(),rowCountOnly:!0};this.$http.post("/api/2021-01/".concat(this.api.value,"/get/"),{data:n}).then((function(e){t.page.url=t.api.value+JSON.stringify(n.filterModel),t.rowCount=e.data.rowCount}))}},getApiList:function(){var e=this;this.$http.get("/api/list/",{}).then((function(t){e.apiList=t.data}))},exportExcelFile:function(){this.gridOptions.api.exportDataAsExcel({sheetName:"PrelimFile.xlsx"})}}},h=g,v=i("2877"),m=Object(v["a"])(h,c,p,!1,null,null,null),b=m.exports;i("5363");u.a.defaults.xsrfCookieName="csrftoken",u.a.defaults.xsrfHeaderName="X-CSRFTOKEN",n["default"].prototype.$http=u.a.create({baseURL:"http://localhost:8000/"}),n["default"].config.productionTip=!1,new n["default"]({axios:u.a,vuetify:l,render:function(e){return e(b)}}).$mount("#report-app")}});