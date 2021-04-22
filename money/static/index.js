import Vue from 'vue'
// import Vuetify from 'vuetify/lib/framework';

import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

import vuetify from '../../src/plugins/vuetify'

function component() {
  const element = document.createElement('div');
  element.innerHTML = 'Hello webpack';
  
    new Vue({
        el: '#app',
        delimiters: ['[[', ']]'],
        vuetify: new Vuetify(),
    })
  

    Vue.use(Vuetify)

    const opts = {}


  return element;
}
document.body.appendChild(component());
export default new Vuetify(opts)
