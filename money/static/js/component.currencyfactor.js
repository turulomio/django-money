/* 
    This class is used as a currency factor input in django
    tags:
        - from. Currency ID: EUR, USD, ...
        - to. Currency ID
        - fromvalue. float Default 1
        - tovalue. float Default 1
        
*/
class InputCurrencyFactor extends HTMLInputElement {
    constructor() {
        super();
    }

    connectedCallback(){
        if (this.hasAttribute("from")){// Doesn't work in constructor and I don't know why.
            this.from=this.getAttribute("from");
        } else {
            alert("You must set 'from' attribute");
        }
        if (this.hasAttribute("from")){// Doesn't work in constructor and I don't know why.
            this.to=this.getAttribute("to");
        } else {
            alert("You must set 'to' attribute");
        }
    
        this.parentNode.style.display="flex";//td
        this.div=document.createElement("div")
        this.div.hidden=true;
        this.button=document.createElement("button");
        this.button.setAttribute("type","button");
        this.button.innerHTML=">";
        this.button.addEventListener("click", (event) => {
            this.changeDisplay();
        });

        this.inputfrom=document.createElement("input");

        if (this.hasAttribute("fromvalue")){// Doesn't work in constructor and I don't know why.
            this.inputfrom.vallue=this.getAttribute("fromvalue");
        } else {
            this.inputfrom.value=1;
        }
        this.inputfrom.addEventListener('change', (event) => {
            this.calculate();
        });
        
        this.labelfrom=document.createElement("label");
        this.labelfrom.innerHTML=this.currency_symbol(this.from);

        this.inputto=document.createElement("input");
        if (this.hasAttribute("tovalue")){// Doesn't work in constructor and I don't know why.
            this.inputto.vallue=this.getAttribute("tovalue");
        } else {
            this.inputto.value=1;
        }
        this.inputto.addEventListener('change', (event) => {
            this.calculate();
        });

        this.labelto=document.createElement("label");
        this.labelto.innerHTML=this.currency_symbol(this.to);
        
        this.div.appendChild(this.inputfrom);
        this.div.appendChild(this.labelfrom);
        this.div.appendChild(this.inputto);
        this.div.appendChild(this.labelto);
        this.div.style.display="flex";

        this.insertAdjacentElement("afterend", this.button);
        this.button.insertAdjacentElement("afterend",this.div);
        
        this.calculate();
    }

    calculate(){
        this.value=parseFloat(this.inputfrom.value/this.inputto.value).toFixed(10);
    }

    currency_symbol(currency){
        if (currency=="EUR"){
            return "€";
        } else if (currency=="USD") {
            return "$";
        } else {
            return "???";
        }
    }

  changeDisplay(){
    if (this.div.hidden==true){
      this.hidden=true;
      this.div.hidden=false;
      this.button.innerHTML="<";
    } else {
      this.hidden=false;
      this.div.hidden=true;
      this.button.innerHTML=">";
    }
  }
};

window.customElements.define('input-currency-factor', InputCurrencyFactor, {extends: 'input'});
