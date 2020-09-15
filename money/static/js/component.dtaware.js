
class InputDatetime extends HTMLInputElement {
  constructor() {
    super();
    this.format_naive="YYYY-MM-DD HH:mm:ss";
    this.format_aware="YYYY-MM-DD HH:mm:ssZ";

    this.addEventListener('click', e => this.changeDisplay());
  }

  first_creation(){
  
    if (this.hasAttribute("locale")){// Doesn't work in constructor and I don't know why.
          this.locale=this.getAttribute("locale");
    }else{

      this.locale="en"; //TODO
    }
    if (this.hasAttribute("localzone")){
      this.localzone=this.getAttribute("localzone");
    }else{
      this.localzone="UTC";
    }
    this.div=document.createElement("div")
    this.div.hidden=true;
    
    this.button=document.createElement("button");
    this.button.setAttribute("type","button");
    this.button.innerHTML="<";

    this.input=document.createElement("input");

    this.inputms=document.createElement("input")
    
    this.select=document.createElement("select"); 
    for (let zone of moment.tz.names()) {
      this.select.innerHTML=this.select.innerHTML.concat(`<option value="${zone}">${zone}</option>`);
    }
    this.select.value=this.localzone;
    
    this.select.addEventListener('change', (event) => {
        this.calculate();
    });
    
    this.input.addEventListener('change', (event) => {
        this.calculate();
    });
    
    this.inputms.addEventListener('change', (event) => {
        this.calculate();
    });
    
    this.button.addEventListener("click", (event) => {
      this.div.hidden=true;
      this.calculate();
    });

    this.div.appendChild(this.button);
    this.div.appendChild(this.input);
    this.div.appendChild(this.inputms);
    this.div.appendChild(this.select);
    this.div.style.display="flex";

    jQuery(this.input).datetimepicker({
      inline:false,
      format:'Y-m-d H:i:s',
    });
    $.datetimepicker.setLocale(this.locale);

    this.insertAdjacentElement("afterend",this.div) ;
  }

  calculate(){
    var dtaware=moment.tz(this.input.value, this.select.value);
    var date=dtaware.format("YYYY-MM-DD HH:mm:ss");
    var tz=dtaware.format("Z");
    this.value=date.concat(".")+this.inputms.value + tz;
  }

  changeDisplay(){  
    if (this.hasOwnProperty( "div")==false){
      this.first_creation();
    } 
    if (this.div.hidden==true){
      //Parse string datetime
      var spl=this.value.split(".");
      console.log(this.value);
      console.log(spl);
      if (spl.length==0){//Without ms 
        var dt=this.value.substring(0,18);
        var ms=0;
      } else {
        var dt=spl[0];
        var ms=spl[1].split("+")[0];        
      }
      this.input.value=dt;
      this.inputms.value=ms;
      this.div.hidden=false;
    } else {
      this.div.hidden=true;
    }
  }
}

window.customElements.define('input-datetime', InputDatetime, {extends: 'input'});
