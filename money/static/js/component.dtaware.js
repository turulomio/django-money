
class InputDatetime extends HTMLInputElement {
  constructor() {
    super();
    this.format_naive="YYYY-MM-DD HH:mm:ss";
    this.format_aware="YYYY-MM-DD HH:mm:ssZ";

    this.addEventListener('click', e => this.changeDisplay());
  }

  first_creation(){
    if (this.hasAttribute("locale")==true){
      this.locale=this.getAttribute("locale");
    }else{

      this.locale="en"; //TODO
    }
    if (this.hasAttribute("localzone")==true){
      this.localzone=this.getAttribute("localzone");
    }else{
      this.localzone="UTC";

    }
    this.div=document.createElement("div")
    this.div.hidden=true;
    
    this.button=document.createElement("button");
    this.button.setAttribute("type","button");
    this.button.innerHTML="<"; 
    this.button.addEventListener("click", (event) => {
      this.div.hidden=true;
      this.value=this.widget2string();
    });

    this.buttonToday=document.createElement("button");
    this.buttonToday.setAttribute("type","button");
    this.buttonToday.innerHTML="Today";
    this.buttonToday.addEventListener("click", (event) => {
      var dtaware=moment.tz();
      this.string2widget(dtaware.format("YYYY-MM-DD HH:mm:ss"));
      this.value=this.widget2string();
      
    });


    this.input=document.createElement("input");
    this.input.addEventListener('change', (event) => {
      this.value=this.widget2string();
    });

    this.inputms=document.createElement("input")
    this.inputms.addEventListener('change', (event) => {
      this.value=this.widget2string();
    });

    this.select=document.createElement("select"); 
    for (let zone of moment.tz.names()) {
      this.select.innerHTML=this.select.innerHTML.concat(`<option value="${zone}">${zone}</option>`);
    }
    this.select.addEventListener('change', (event) => {
      this.value=this.widget2string();
    });
    this.select.value=this.localzone;

    this.div.appendChild(this.button);
    this.div.appendChild(this.input);
    this.div.appendChild(this.inputms);
    this.div.appendChild(this.select);
    this.div.appendChild(this.buttonToday);
    this.div.style.display="flex";

    jQuery(this.input).datetimepicker({
      inline:false,
      format:'Y-m-d H:i:s',
      lang: this.locale,
    });

    this.insertAdjacentElement("afterend",this.div) ;
  }
  widget2string(){
    var dtaware=moment.tz(this.input.value, this.select.value);
    var date=dtaware.format("YYYY-MM-DD HH:mm:ss");
    var tz=dtaware.format("Z");
    return date.concat(".")+this.inputms.value + tz;
  }

  string2widget(s){
    var spl=s.split(".");
    if (spl.length==1){//Without ms 
      var dt=s.substring(0,19);
      var ms=0;
    } else {
        var dt=spl[0];
        var ms=spl[1].split("+")[0];        
    }
    this.input.value=dt;
    this.inputms.value=ms;
  }

  changeDisplay(){  
    if (this.hasOwnProperty( "div")==false){
      this.first_creation();
    } 
    if (this.div.hidden==true){
      this.string2widget(this.value);
      this.div.hidden=false;
    } else {
      this.div.hidden=true;
    }
  }
}

window.customElements.define('input-datetime', InputDatetime, {extends: 'input'});
