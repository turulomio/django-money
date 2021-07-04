!function(n,e){"object"==typeof exports&&"undefined"!=typeof module?e(exports,require("vue")):"function"==typeof define&&define.amd?define(["exports","vue"],e):e((n="undefined"!=typeof globalThis?globalThis:n||self).VueCompositionAPI={},n.Vue)}(this,(function(n,e){"use strict";function t(n){return n&&"object"==typeof n&&"default"in n?n:{default:n}}var r=t(e);function o(n){return"function"==typeof n&&/native code/.test(n.toString())}var i="undefined"!=typeof Symbol&&o(Symbol)&&"undefined"!=typeof Reflect&&o(Reflect.ownKeys),u=function(n){return n};function a(n,e,t){var r=t.get,o=t.set;Object.defineProperty(n,e,{enumerable:!0,configurable:!0,get:r||u,set:o||u})}function f(n,e,t,r){Object.defineProperty(n,e,{value:t,enumerable:!!r,writable:!0,configurable:!0})}function c(n,e){return Object.hasOwnProperty.call(n,e)}function l(n){return Array.isArray(n)}var s=Object.prototype.toString,v=function(n){return s.call(n)};function d(n){var e=parseFloat(String(n));return e>=0&&Math.floor(e)===e&&isFinite(n)&&e<=4294967295}function p(n){return null!==n&&"object"==typeof n}function y(n){return"[object Object]"===function(n){return Object.prototype.toString.call(n)}(n)}function _(n){return"function"==typeof n}function b(n,e){r.default.util.warn(n,e)}var h=void 0;try{var g=require("vue");g&&$(g)?h=g:g&&"default"in g&&$(g.default)&&(h=g.default)}catch(n){}var m=null,w=null,j="__composition_api_installed__";function $(n){return n&&"function"==typeof n&&"Vue"===n.name}function O(){return m}function x(n){w=n}function S(){return w?M(w):null}var k,E=new WeakMap;function M(n){if(E.has(n))return E.get(n);var e={proxy:n,update:n.$forceUpdate,uid:n._uid,emit:n.$emit.bind(n),parent:null,root:null};return["data","props","attrs","refs","vnode","slots"].forEach((function(t){a(e,t,{get:function(){return n["$"+t]}})})),a(e,"isMounted",{get:function(){return n._isMounted}}),a(e,"isUnmounted",{get:function(){return n._isDestroyed}}),a(e,"isDeactivated",{get:function(){return n._inactive}}),a(e,"emitted",{get:function(){return n._events}}),E.set(n,e),n.$parent&&(e.parent=M(n.$parent)),n.$root&&(e.root=M(n.$root)),e}function R(n){var e=S();return null==e?void 0:e.proxy}function C(n,e){void 0===e&&(e={});var t=n.config.silent;n.config.silent=!0;var r=new n(e);return n.config.silent=t,r}function A(n,e){return function(){for(var t=[],r=0;r<arguments.length;r++)t[r]=arguments[r];return n.$scopedSlots[e]?n.$scopedSlots[e].apply(n,t):b("slots."+e+'() got called outside of the "render()" scope',n)}}var P=function(){return(P=Object.assign||function(n){for(var e,t=1,r=arguments.length;t<r;t++)for(var o in e=arguments[t])Object.prototype.hasOwnProperty.call(e,o)&&(n[o]=e[o]);return n}).apply(this,arguments)};
/*! *****************************************************************************
  Copyright (c) Microsoft Corporation.

  Permission to use, copy, modify, and/or distribute this software for any
  purpose with or without fee is hereby granted.

  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
  REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
  AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
  INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
  LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
  OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
  PERFORMANCE OF THIS SOFTWARE.
  ***************************************************************************** */function D(n){var e="function"==typeof Symbol&&Symbol.iterator,t=e&&n[e],r=0;if(t)return t.call(n);if(n&&"number"==typeof n.length)return{next:function(){return n&&r>=n.length&&(n=void 0),{value:n&&n[r++],done:!n}}};throw new TypeError(e?"Object is not iterable.":"Symbol.iterator is not defined.")}function U(n,e){var t="function"==typeof Symbol&&n[Symbol.iterator];if(!t)return n;var r,o,i=t.call(n),u=[];try{for(;(void 0===e||e-- >0)&&!(r=i.next()).done;)u.push(r.value)}catch(n){o={error:n}}finally{try{r&&!r.done&&(t=i.return)&&t.call(i)}finally{if(o)throw o.error}}return u}function V(n,e){for(var t=0,r=e.length,o=n.length;t<r;t++,o++)n[o]=e[t];return n}function W(n){return i?Symbol.for(n):n}var B=W("composition-api.preFlushQueue"),T=W("composition-api.postFlushQueue"),z="composition-api.refKey",I=new WeakMap,F=new WeakMap,K=new WeakMap,q=function(n){a(this,"value",{get:n.get,set:n.set})};function J(n,e){var t=new q(n),r=Object.seal(t);return K.set(r,!0),r}function N(n){var e;if(Q(n))return n;var t=un(((e={})[z]=n,e));return J({get:function(){return t[z]},set:function(n){return t[z]=n}})}function Q(n){return n instanceof q}function G(n){return Q(n)?n.value:n}function H(n){if(!y(n))return n;var e={};for(var t in n)e[t]=L(n,t);return e}function L(n,e){var t=n[e];return Q(t)?t:J({get:function(){return n[e]},set:function(t){return n[e]=t}})}function X(n){var e;return Boolean(n&&c(n,"__ob__")&&"object"==typeof n.__ob__&&(null===(e=n.__ob__)||void 0===e?void 0:e.__raw__))}function Y(n){var e;return Boolean(n&&c(n,"__ob__")&&"object"==typeof n.__ob__&&!(null===(e=n.__ob__)||void 0===e?void 0:e.__raw__))}function Z(n){if(!(!y(n)||X(n)||Array.isArray(n)||Q(n)||function(n){var e=O();return e&&n instanceof e}(n)||I.has(n))){I.set(n,!0);for(var e=Object.keys(n),t=0;t<e.length;t++)nn(n,e[t])}}function nn(n,e,t){if("__ob__"!==e&&!X(n[e])){var r,o,i=Object.getOwnPropertyDescriptor(n,e);if(i){if(!1===i.configurable)return;r=i.get,o=i.set,r&&!o||2!==arguments.length||(t=n[e])}Z(t),a(n,e,{get:function(){var o=r?r.call(n):t;return e!==z&&Q(o)?o.value:o},set:function(i){if(!r||o){var u=r?r.call(n):t;e!==z&&Q(u)&&!Q(i)?u.value=i:o?o.call(n,i):t=i,Z(i)}}})}}function en(n){var e,t=m||h;t.observable?e=t.observable(n):e=C(t,{data:{$$state:n}})._data.$$state;return c(e,"__ob__")||tn(e),e}function tn(n,e){var t,r;if(void 0===e&&(e=new WeakMap),!e.has(n)){f(n,"__ob__",function(n){void 0===n&&(n={});return{value:n,dep:{notify:u,depend:u,addSub:u,removeSub:u}}}(n)),e.set(n,!0);try{for(var o=D(Object.keys(n)),i=o.next();!i.done;i=o.next()){var a=n[i.value];(y(a)||l(a))&&!X(a)&&Object.isExtensible(a)&&tn(a)}}catch(n){t={error:n}}finally{try{i&&!i.done&&(r=o.return)&&r.call(o)}finally{if(t)throw t.error}}}}function rn(){return en({}).__ob__}function on(n){var e,t;if(!p(n))return n;if(!y(n)&&!l(n)||X(n)||!Object.isExtensible(n))return n;var r=en(l(n)?[]:{});Z(r);var o=r.__ob__,i=function(e){var t,i,u=n[e],f=Object.getOwnPropertyDescriptor(n,e);if(f){if(!1===f.configurable)return"continue";t=f.get,i=f.set}a(r,e,{get:function(){var e,r=t?t.call(n):u;return null===(e=o.dep)||void 0===e||e.depend(),r},set:function(e){var r;t&&!i||(i?i.call(n,e):u=e,null===(r=o.dep)||void 0===r||r.notify())}})};try{for(var u=D(Object.keys(n)),f=u.next();!f.done;f=u.next()){i(f.value)}}catch(n){e={error:n}}finally{try{f&&!f.done&&(t=u.return)&&t.call(u)}finally{if(e)throw e.error}}return r}function un(n){if(!p(n))return n;if(!y(n)&&!l(n)||X(n)||!Object.isExtensible(n))return n;var e=en(n);return Z(e),e}function an(n){return function(e){var t,r=R(((t=n)[0].toUpperCase(),t.slice(1)));r&&function(n,e,t,r){var o=e.$options,i=n.config.optionMergeStrategies[t];o[t]=i(o[t],function(n,e){return function(){for(var t,r=[],o=0;o<arguments.length;o++)r[o]=arguments[o];var i=null===(t=S())||void 0===t?void 0:t.proxy;x(n);try{return e.apply(void 0,V([],U(r)))}finally{x(i)}}}(e,r))}(O(),r,n,e)}}var fn,cn=an("beforeMount"),ln=an("mounted"),sn=an("beforeUpdate"),vn=an("updated"),dn=an("beforeDestroy"),pn=an("destroyed"),yn=an("errorCaptured"),_n=an("activated"),bn=an("deactivated"),hn=an("serverPrefetch");function gn(){jn(this,B)}function mn(){jn(this,T)}function wn(){var n,e=null===(n=S())||void 0===n?void 0:n.proxy;return e?function(n){return void 0!==n[B]}(e)||function(n){n[B]=[],n[T]=[],n.$on("hook:beforeUpdate",gn),n.$on("hook:updated",mn)}(e):(fn||(fn=C(O())),e=fn),e}function jn(n,e){for(var t=n[e],r=0;r<t.length;r++)t[r]();t.length=0}function $n(n,e,t){var r=function(){n.$nextTick((function(){n[B].length&&jn(n,B),n[T].length&&jn(n,T)}))};switch(t){case"pre":r(),n[B].push(e);break;case"post":r(),n[T].push(e);break;default:!function(n,e){if(!n)throw new Error("[vue-composition-api] "+e)}(!1,'flush must be one of ["post", "pre", "sync"], but got '+t)}}function On(n,e){var t=n.teardown;n.teardown=function(){for(var r=[],o=0;o<arguments.length;o++)r[o]=arguments[o];t.apply(n,r),e()}}function xn(n,e,t,r){var o,i,a=r.flush,f="sync"===a,c=function(n){i=function(){try{n()}catch(n){!function(n,e,t){if("undefined"==typeof window||"undefined"==typeof console)throw n;console.error(n)}(n)}}},s=function(){i&&(i(),i=null)},v=function(e){return f||n===fn?e:function(){for(var t=[],r=0;r<arguments.length;r++)t[r]=arguments[r];return $n(n,(function(){e.apply(void 0,V([],U(t)))}),a)}};if(null===t){var d=!1,p=function(n,e,t,r){var o=n._watchers.length;return n.$watch(e,t,{immediate:r.immediateInvokeCallback,deep:r.deep,lazy:r.noRun,sync:r.sync,before:r.before}),n._watchers[o]}(n,(function(){if(!d)try{d=!0,e(c)}finally{d=!1}}),u,{deep:r.deep||!1,sync:f,before:s});On(p,s),p.lazy=!1;var y=p.get.bind(p);return p.get=v(y),function(){p.teardown()}}var h,g=r.deep;Q(e)?h=function(){return e.value}:Y(e)?(h=function(){return e},g=!0):l(e)?h=function(){return e.map((function(e){return Q(e)?e.value:Y(e)?Sn(e):_(e)?e():(b("Invalid watch source: "+JSON.stringify(e)+".\n          A watch source can only be a getter/effect function, a ref, a reactive object, or an array of these types.",n),u)}))}:_(e)?h=e:(h=u,b("Invalid watch source: "+JSON.stringify(e)+".\n      A watch source can only be a getter/effect function, a ref, a reactive object, or an array of these types.",n));var m=function(n,e){s(),t(n,e,c)},w=v(m);if(r.immediate){var j=w,$=function(n,e){$=j,m(n,l(n)?[]:e)};w=function(n,e){$(n,e)}}var O=n.$watch(h,w,{immediate:r.immediate,deep:g,sync:f}),x=n._watchers[n._watchers.length-1];return Y(x.value)&&(null===(o=x.value.__ob__)||void 0===o?void 0:o.dep)&&g&&x.value.__ob__.dep.addSub({update:function(){x.run()}}),On(x,s),function(){O()}}function Sn(n,e){if(void 0===e&&(e=new Set),!p(n)||e.has(n))return n;if(e.add(n),Q(n))Sn(n.value,e);else if(l(n))for(var t=0;t<n.length;t++)Sn(n[t],e);else if("[object Set]"===v(n)||function(n){return"[object Map]"===v(n)}(n))n.forEach((function(n){Sn(n,e)}));else if(y(n))for(var r in n)Sn(n[r],e);return n}var kn={};var En={},Mn=function(n){var e;void 0===n&&(n="$style");var t=S();if(!t)return En;var r=null===(e=t.proxy)||void 0===e?void 0:e[n];return r||En},Rn=Mn;var Cn;var An={set:function(n,e,t){(n.__composition_api_state__=n.__composition_api_state__||{})[e]=t},get:function(n,e){return(n.__composition_api_state__||{})[e]}};function Pn(n){var e=An.get(n,"rawBindings")||{};if(e&&Object.keys(e).length){for(var t=n.$refs,r=An.get(n,"refs")||[],o=0;o<r.length;o++){var i=e[f=r[o]];!t[f]&&i&&Q(i)&&(i.value=null)}var u=Object.keys(t),a=[];for(o=0;o<u.length;o++){var f;i=e[f=u[o]];t[f]&&i&&Q(i)&&(i.value=t[f],a.push(f))}An.set(n,"refs",a)}}function Dn(n,e){var t=n.$options._parentVnode;if(t){for(var r=An.get(n,"slots")||[],o=function(n,e){var t;if(n){if(n._normalized)return n._normalized;for(var r in t={},n)n[r]&&"$"!==r[0]&&(t[r]=!0)}else t={};for(var r in e)r in t||(t[r]=!0);return t}(t.data.scopedSlots,n.$slots),i=0;i<r.length;i++){o[a=r[i]]||delete e[a]}var u=Object.keys(o);for(i=0;i<u.length;i++){var a;e[a=u[i]]||(e[a]=A(n,a))}An.set(n,"slots",u)}}function Un(n,e,t){var r=w;x(n);try{return e(n)}catch(n){if(!t)throw n;t(n)}finally{x(r)}}function Vn(n){function e(n){if(y(n)&&!Q(n)&&!Y(n)&&!X(n)){var t=O().util.defineReactive;Object.keys(n).forEach((function(r){var o=n[r];t(n,r,o),o&&e(o)}))}}function t(n,e){return void 0===e&&(e=new Map),e.has(n)?e.get(n):(e.set(n,!1),Array.isArray(n)&&Y(n)?(e.set(n,!0),!0):!(!y(n)||X(n))&&Object.keys(n).some((function(r){return t(n[r],e)})))}n.mixin({beforeCreate:function(){var n=this,r=n.$options,o=r.setup,i=r.render;i&&(r.render=function(){for(var e=this,t=[],r=0;r<arguments.length;r++)t[r]=arguments[r];return Un(n,(function(){return i.apply(e,t)}))});if(!o)return;if("function"!=typeof o)return;var u=r.data;r.data=function(){return function(n,r){void 0===r&&(r={});var o,i=n.$options.setup,u=function(n){var e={slots:{}},t=["attrs"],r=["emit"];return["root","parent","refs","listeners","isServer","ssrContext"].forEach((function(t){var r="$"+t;a(e,t,{get:function(){return n[r]},set:function(){b("Cannot assign to '"+t+"' because it is a read-only property",n)}})})),t.forEach((function(t){var r="$"+t;a(e,t,{get:function(){var e,t,o=un({}),i=n[r],u=function(e){a(o,e,{get:function(){return n[r][e]}})};try{for(var f=D(Object.keys(i)),c=f.next();!c.done;c=f.next()){u(c.value)}}catch(n){e={error:n}}finally{try{c&&!c.done&&(t=f.return)&&t.call(f)}finally{if(e)throw e.error}}return o},set:function(){b("Cannot assign to '"+t+"' because it is a read-only property",n)}})})),r.forEach((function(t){var r="$"+t;a(e,t,{get:function(){return function(){for(var e=[],t=0;t<arguments.length;t++)e[t]=arguments[t];n[r].apply(n,e)}}})})),e}(n);if(f(r,"__ob__",rn()),Dn(n,u.slots),Un(n,(function(){o=i(r,u)})),!o)return;if(_(o)){var s=o;return void(n.$options.render=function(){return Dn(n,u.slots),Un(n,(function(){return s()}))})}if(y(o)){Y(o)&&(o=H(o)),An.set(n,"rawBindings",o);var v=o;Object.keys(v).forEach((function(r){var o=v[r];Q(o)||(Y(o)?l(o)&&(o=N(o)):_(o)?o=o.bind(n):p(o)?t(o)&&e(o):o=N(o)),function(n,e,t){var r=n.$options.props;e in n||r&&c(r,e)||(Q(t)?a(n,e,{get:function(){return t.value},set:function(n){t.value=n}}):a(n,e,{get:function(){return Y(t)&&t.__ob__.dep.depend(),t},set:function(n){t=n}}))}(n,r,o)}))}}(n,n.$props),"function"==typeof u?u.call(n,n):u||{}}},mounted:function(){Pn(this)},updated:function(){Pn(this)}})}function Wn(n,e){if(!n)return e;if(!e)return n;for(var t,r,o,u=i?Reflect.ownKeys(n):Object.keys(n),a=0;a<u.length;a++)"__ob__"!==(t=u[a])&&(r=e[t],o=n[t],c(e,t)?r!==o&&y(r)&&!Q(r)&&y(o)&&!Q(o)&&Wn(o,r):e[t]=o);return e}function Bn(n){(function(n){return c(n,j)})(n)||(n.config.optionMergeStrategies.setup=function(n,e){return function(t,r){return Wn("function"==typeof n?n(t,r)||{}:void 0,"function"==typeof e?e(t,r)||{}:void 0)}},function(n){m=n,Object.defineProperty(n,j,{configurable:!0,writable:!0,value:!0})}(n),Vn(n))}var Tn={install:function(n){return Bn(n)}};"undefined"!=typeof window&&window.Vue&&window.Vue.use(Tn),n.computed=function(n){var e,t,r,o,i,a=null===(e=S())||void 0===e?void 0:e.proxy;if("function"==typeof n?t=n:(t=n.get,r=n.set),a&&!a.$isServer){var f,c=function(){if(!k){var n=C(O(),{computed:{value:function(){return 0}}}),e=n._computedWatchers.value.constructor,t=n._data.__ob__.dep.constructor;k={Watcher:e,Dep:t},n.$destroy()}return k}(),l=c.Watcher,s=c.Dep;i=function(){return f||(f=new l(a,t,u,{lazy:!0})),f.dirty&&f.evaluate(),s.target&&f.depend(),f.value},o=function(n){r&&r(n)}}else{var v=C(O(),{computed:{$$state:{get:t,set:r}}});a&&a.$on("hook:destroyed",(function(){return v.$destroy()})),i=function(){return v.$$state},o=function(n){v.$$state=n}}return J({get:i,set:o})},n.createApp=function(n,e){void 0===e&&(e=void 0);var t=O(),r=void 0;return{config:t.config,use:t.use.bind(t),mixin:t.mixin.bind(t),component:t.component.bind(t),directive:t.directive.bind(t),mount:function(o,i){return r||((r=new t(P({propsData:e},n))).$mount(o,i),r)},unmount:function(){r&&(r.$destroy(),r=void 0)}}},n.createRef=J,n.customRef=function(n){var e=N(0);return J(n((function(){e.value}),(function(){++e.value})))},n.default=Tn,n.defineAsyncComponent=function(n){_(n)&&(n={loader:n});var e=n.loader,t=n.loadingComponent,r=n.errorComponent,o=n.delay,i=void 0===o?200:o,u=n.timeout;n.suspensible;var a=n.onError,f=null,c=0,l=function(){var n;return f||(n=f=e().catch((function(n){if(n=n instanceof Error?n:new Error(String(n)),a)return new Promise((function(e,t){a(n,(function(){return e((c++,f=null,l()))}),(function(){return t(n)}),c+1)}));throw n})).then((function(e){return n!==f&&f?f:(e&&(e.__esModule||"Module"===e[Symbol.toStringTag])&&(e=e.default),e)})))};return function(){return{component:l(),delay:i,timeout:u,error:r,loading:t}}},n.defineComponent=function(n){return n},n.del=function(n,e){if(O().util.warn,Array.isArray(n)&&d(e))n.splice(e,1);else{var t=n.__ob__;n._isVue||t&&t.vmCount||c(n,e)&&(delete n[e],t&&t.dep.notify())}},n.getCurrentInstance=S,n.h=function(){for(var n,e=[],t=0;t<arguments.length;t++)e[t]=arguments[t];var r=null===(n=S())||void 0===n?void 0:n.proxy;return r?r.$createElement.apply(r,e):(b("`createElement()` has been called outside of render function."),Cn||(Cn=C(O()).$createElement),Cn.apply(Cn,e))},n.inject=function(n,e,t){var r;if(void 0===t&&(t=!1),!n)return e;var o=null===(r=S())||void 0===r?void 0:r.proxy;if(o){var i=function(n,e){for(var t=e;t;){if(t._provided&&c(t._provided,n))return t._provided[n];t=t.$parent}return kn}(n,o);return i!==kn?i:t&&_(e)?e():e}b("inject() can only be used inside setup() or functional components.")},n.isRaw=X,n.isReactive=Y,n.isReadonly=function(n){return K.has(n)},n.isRef=Q,n.markRaw=function(n){if(!y(n)&&!l(n)||!Object.isExtensible(n))return n;var e=rn();return e.__raw__=!0,f(n,"__ob__",e),F.set(n,!0),n},n.nextTick=function(){for(var n,e=[],t=0;t<arguments.length;t++)e[t]=arguments[t];return null===(n=O())||void 0===n?void 0:n.nextTick.apply(this,e)},n.onActivated=_n,n.onBeforeMount=cn,n.onBeforeUnmount=dn,n.onBeforeUpdate=sn,n.onDeactivated=bn,n.onErrorCaptured=yn,n.onMounted=ln,n.onServerPrefetch=hn,n.onUnmounted=pn,n.onUpdated=vn,n.provide=function(n,e){var t=R();if(t){if(!t._provided){var r={};a(t,"_provided",{get:function(){return r},set:function(n){return Object.assign(r,n)}})}t._provided[n]=e}},n.proxyRefs=function(n){var e,t,r;if(Y(n))return n;var o=un(((e={})[z]=n,e)),i=function(n){a(o,n,{get:function(){return Q(o[z][n])?o[z][n].value:o[z][n]},set:function(e){if(Q(o[z][n]))return o[z][n].value=G(e);o[z][n]=G(e)}})};try{for(var u=D(Object.keys(n)),f=u.next();!f.done;f=u.next()){i(f.value)}}catch(n){t={error:n}}finally{try{f&&!f.done&&(r=u.return)&&r.call(u)}finally{if(t)throw t.error}}return o},n.reactive=un,n.readonly=function(n){return n},n.ref=N,n.set=function(n,e,t){var r,o=O().util;o.warn;var i=o.defineReactive;if(l(n)){if(d(e))return n.length=Math.max(n.length,e),n.splice(e,1,t),t;if("length"===e&&t!==n.length)return n.length=t,null===(r=n.__ob__)||void 0===r||r.dep.notify(),t}if(e in n&&!(e in Object.prototype))return n[e]=t,t;var u=n.__ob__;return n._isVue||u&&u.vmCount?t:u?(i(u.value,e,t),nn(n,e,t),u.dep.notify(),t):(n[e]=t,t)},n.shallowReactive=on,n.shallowReadonly=function(n){var e,t;if(!p(n))return n;if(!y(n)&&!l(n)||!Object.isExtensible(n)&&!Q(n))return n;var r=Q(n)?new q({}):Y(n)?en({}):{},o=un({}).__ob__,i=function(e){var t,i=n[e],u=Object.getOwnPropertyDescriptor(n,e);if(u){if(!1===u.configurable&&!Q(n))return"continue";t=u.get}a(r,e,{get:function(){var e=t?t.call(n):i;return o.dep.depend(),e},set:function(n){}})};try{for(var u=D(Object.keys(n)),f=u.next();!f.done;f=u.next()){i(f.value)}}catch(n){e={error:n}}finally{try{f&&!f.done&&(t=u.return)&&t.call(u)}finally{if(e)throw e.error}}return K.set(r,!0),r},n.shallowRef=function(n){var e;if(Q(n))return n;var t=on(((e={})[z]=n,e));return J({get:function(){return t[z]},set:function(n){return t[z]=n}})},n.toRaw=function(n){var e,t;return X(n)||!Object.isExtensible(n)?n:(null===(t=null===(e=n)||void 0===e?void 0:e.__ob__)||void 0===t?void 0:t.value)||n},n.toRef=L,n.toRefs=H,n.triggerRef=function(n){Q(n)&&(n.value=n.value)},n.unref=G,n.useCSSModule=Rn,n.useCssModule=Mn,n.version="1.0.0-rc.13",n.warn=function(n){var e;b(n,null===(e=S())||void 0===e?void 0:e.proxy)},n.watch=function(n,e,t){var r=null;"function"==typeof e?r=e:(t=e,r=null);var o=function(n){return P({immediate:!1,deep:!1,flush:"pre"},n)}(t);return xn(wn(),n,r,o)},n.watchEffect=function(n,e){var t=function(n){return P({immediate:!0,deep:!1,flush:"pre"},n)}(e);return xn(wn(),n,null,t)},Object.defineProperty(n,"__esModule",{value:!0})}));
