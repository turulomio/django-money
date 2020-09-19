
class InputDate extends HTMLInputElement {
  constructor() {
    super();   
    jQuery(this).datetimepicker({
      inline:false,
      format:'Y-m-d',
      timepicker:false,
    });
    this.addEventListener('click', e => this.changeDisplay());
  }

  first_creation(){
    if (this.hasAttribute("locale")){// Doesn't work in constructor and I don't know why.
        this.locale=this.getAttribute("locale");
    }else{
        this.locale="en";
    }
    $.datetimepicker.setLocale(this.locale);

  }

  changeDisplay(){
    if (this.hasOwnProperty( "locale")==false){
      this.first_creation();
    } 
  }
}

window.customElements.define('input-date', InputDate, {extends: 'input'});
