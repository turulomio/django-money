
class InputDatetime extends HTMLElement {
  constructor() {
    super();
    this.format_naive="YYYY-MM-DD HH:mm:ss";
    this.format_aware="YYYY-MM-DD HH:mm:ssZ";
    this.dtaware=null;
  }

  connectedCallback(){   
    if (this.hasAttribute("locale")==true){
        moment.locale(this.getAttribute("locale"));
    }
    this.input=document.createElement("input");
    this.input.setAttribute("id","datetimepicker1")
    this.input.addEventListener('change', (event) => {
        this.calculate();
    });
    //let shadow = this.input.attachShadow({mode: 'open'});

    if (this.hasAttribute("datetime")==true){
        this.input.value=this.getAttribute("datetime");
    } else{
      this.input.value=moment().format(this.format_naive);
    }

    if (this.hasAttribute("parent_id")==true){
        this.parent=document.getElementById(this.getAttribute("parent_id"));
    } else{
      this.parent=null;
    }

    this.selTimezone=document.createElement("select");
    for (let zone of moment.tz.names()) {
        this.selTimezone.innerHTML=this.selTimezone.innerHTML.concat(`<option value="${zone}">${zone}</option>`);
    }
    if (this.hasAttribute("timezone")==true){
      this.selTimezone.value=this.getAttribute("timezone");
    } else{
      this.selTimezone.value='UTC';
    }

    this.selTimezone.addEventListener('change', (event) => {
        this.calculate();
    });
    this.appendChild(this.input);
    this.appendChild(this.selTimezone);
    this.calculate();
  }

  calculate(){
      var old=this.dtaware;
      this.dtaware=moment.tz(this.input.value, this.selTimezone.value);
      if (old != this.dtaware){
        let event = new Event("changed");
        this.dispatchEvent(event);
        this.parent.value=this.dtaware.format(this.format_aware);

      }
  }
  getValue(){
      return this.label.innerHTML;
  }

}

window.customElements.define('input-datetime', InputDatetime);
