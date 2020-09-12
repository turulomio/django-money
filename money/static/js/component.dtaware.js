
class InputDatetime extends HTMLElement {
  constructor() {
    super();
    this.format_naive="YYYY-MM-DD HH:mm:ss";
    this.format_aware="YYYY-MM-DD HH:mm:ssZ";
  }

  connectedCallback(){   
    if (this.hasAttribute("locale")==true){
        moment.locale(this.getAttribute("locale"));
    }

    this.label=document.createElement("label")

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
    this.appendChild(this.label);
    this.calculate();
  }

  calculate(){
      var old=this.label.innerHTML;
      var dtaware=moment.tz(this.input.value, this.selTimezone.value);
      this.label.innerHTML=dtaware.format(this.format_aware);
      if (old != this.label.innerHTML){
        let event = new Event("changed");
        this.dispatchEvent(event);

      }
  }
  getValue(){
      return this.label.innerHTML;
  }

}

window.customElements.define('input-datetime', InputDatetime);
