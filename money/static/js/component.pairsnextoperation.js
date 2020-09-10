// This component needs tabulator.min.js and tabulator.min.css

class PairsNextOperation extends HTMLElement {
  constructor() {
    super();
  }
/*
<p><strong>{% trans "Better product has invested" %}: </strong><label id="better_current_nominal">0</label> {{product_better.currency}}</p>
<p><strong>{% trans "Worse product has invested" %} : </strong><label id="better_worst_nominal">0</label> {{product_worse.currency}}</p>
<label>New amount in {{local_currency}}: </label>
<input id="percentage" type="text" name="next" value="15000" onchange="calculate_shares_to_invest();" onkeydown="calculate_shares_to_invest();">
<p><strong>Better reinvest nominal. </strong><label id="better_reinvest_nominal">0</label> {{product_better.currency}}</p>
<p><strong>Worse reinvest nominal. </strong><label id="worse_reinvest_nominal">0</label> {{product_worse.currency}}</p>
<p><strong>Better total new nominal. </strong><label id="better_total_new_nominal">0</label> {{product_better.currency}}</p>
<p><strong>Worse total new nominal. </strong><label id="worse_total_new_nominal">0</label> {{product_worse.currency}}</p>
<p><strong>Better shares amount. </strong><label id="better_reinvest_shares">0</label></p>
<p><strong>Worse shares amount. </strong><label id="worse_reinvest_shares">0</label></p>
<script>
    function calculate_shares_to_invest(){
        var label = document.getElementById('result');
        var input=document.getElementById('percentage');
        var percentage=parseFloat(input.value);
        var shares=parseFloat(label.getAttribute("better_shares"));
        var gains=parseFloat(label.getAttribute("gains"));
        var average_price=parseFloat(label.getAttribute("better_average_price"));
        var leverage=parseFloat(label.getAttribute("better_leverages_real"));
        var diff=shares*average_price*leverage*(percentage/100) ;
        label.innerHTML="".concat(gains).concat("-").concat(diff).concat("=").concat(gains-diff).concat(" {{local_currency}}");
    }
    calculate_reinvest_loses();

</script>*/
  getValue(attribute, default_,type){
    if (this.hasAttribute(attribute)==true){
        var value= this.getAttribute(attribute);
    } else{
      var value=default_;
    }

    if (type=="str"){
      return value;
    }
    else if (type="float"){
      return parseFloat(value);
    }
  }

  connectedCallback(){
    this.better_currency=this.getValue("better_currency", "", "str");
    this.worse_currency=this.getValue("worse_currency", "","str");
    this.label_string=this.getValue("label_string","","str");
    this.default_amount=this.getValue("default_amount","15000","float");
    this.better_current=this.getValue("better_current","0","float");
    this.worse_current=this.getValue("worse_current","0","float");

    this.cmdCalculate=document.createElement("button"); 
    this.cmdCalculate.innerHTML = "Calculate";
    this.cmdCalculate.addEventListener('click', (event) => {
      event.preventDefault();
      $.ajax({
        type: "POST",
        url: "{% url 'report_total_income__div' year %}",
        data: {
              csrfmiddlewaretoken: "{{csrf_token}}",
        },
        success: function(result) {
          $("#income").html(result);    
          $("#form_income").css("display", "none");
  
        },
        error: function(result) {
          $("#income").html('<p>{% trans "Somethng is wrong" %}</p>');          
        }
      });
    });

    this.lbl=document.createElement("label");
    this.lbl.innerHTML=this.label_string;
    this.txtAmount=document.createElement("input");
    this.txtAmount.value=this.default_amount;
    this.div=document.createElement("div");
    this.div.setAttribute("id", "table_div");

    this.p=document.createElement("p")


    this.appendChild(this.lbl);
    this.appendChild(this.txtAmount);
    this.appendChild(this.cmdCalculate);
    this.appendChild(this.p);
    this.appendChild(this.div);
/*    this.tabledata = [
      { 
        'name': 'Better', 
        'current': this.better_current, 
        'invest': -0.89, 
        'total': 3320.4,
        'shares': -29551.5
      },      
      { 
        'name': 'Worse', 
        'current': this.worse_current, 
        'invest': -0.89, 
        'total': 3320.4,
        'shares': -29551.5
      },
    ];  
    this.table = new Tabulator("#table_div", {
      selectable:true,
      data:this.tabledata, //assign data to table
      layout:"fitDataTable", //fit columns to width of table (optional)
      columns:[ 
        {title: "Name", field:"name"}, 
        {title: "Current gross", field:"current"}, 
        {title: "Reinvest gross", field:"invest", hozAlign:"right" }, 
        {title: "Total gross", field:"total", minWidth:100, hozAlign:"right" }, 
        {title: "Shares to invest", field:"shares", minWidth:100, hozAlign:"right"}, 
      ],
    });
  }
<script>
$(document).ready(function() {
  $("#button_income").click(function(e) {

  });
});
</script>

*/


/*
    if (this.hasAttribute("url")==true){
      this.url=this.getAttribute("url");
    } else{
      this.title=null;
    }

    var today=new Date();

    if (this.hasAttribute("year_start")==true){
      this.year_start=parseInt(this.getAttribute("year_start"));
    }else {
      this.year_start=today.getFullYear()-3;
    }

    if (this.hasAttribute("year_end")==true){
      this.year_end=parseInt(this.getAttribute("year_end"));
    }else {
      this.year_end=today.getFullYear()+3;
    }

    if (this.hasAttribute("year")==true){
      this.year=parseInt(this.getAttribute("year"));
    }else {
      this.year=today.getFullYear();
    }    

    this.label=document.createElement("label");
    this.label.innerHTML=this.title + " ";

    this.selYear=document.createElement("select");
    for (var i=0; i< this.year_end-this.year_start+1; i++){
      var option= document.createElement("option");
      option.value=this.year_start + i;
      option.text=this.year_start+i;
      this.selYear.appendChild(option);
    }


    this.cmdYearPrevious=document.createElement("button"); 
    this.cmdYearPrevious.innerHTML = "<";
    this.cmdYearNext=document.createElement("button");
    this.cmdYearNext.innerHTML = ">";
    this.cmdCurrent=document.createElement("button");
    this.cmdCurrent.innerHTML = "Current";
    if (this.url != null){
      this.cmdGo=document.createElement("button");
      this.cmdGo.innerHTML = "Go";

      this.cmdGo.addEventListener('click', (event) => {

        var newurl=this.url.concat(this.year.toString()).concat("/");
        window.location.replace(newurl);
      });
    }



    this.appendChild(this.label);
    this.appendChild(this.cmdYearPrevious);
    this.appendChild(this.selYear);
    this.appendChild(this.cmdYearNext);
    this.appendChild(this.cmdCurrent);
    this.appendChild(this.cmdGo);
    this.selYear.value=this.year;


    this.cmdYearPrevious.addEventListener('click', (event) => {
      this._render(this.year,this.year-1);
    });
    this.cmdYearNext.addEventListener('click', (event) => {
      this._render(this.year,this.year+1);
    });
    this.cmdCurrent.addEventListener('click', (event) => {
        this._render(this.year,today.getFullYear());
    });
    this.selYear.addEventListener('change', (event) => {
        this._render(this.year,this.selYear.value);
    });
    */

  //Try to change or return the old position with an alert
  calculate(){
    alert("hoal");
    /*
    if (new_year>this.year_end){
      this.year=old_year;
      alert("You can't set the next year");
    }
    else if (new_year<this.year_start){
      this.year=old_year;
      alert("You can't set the previous year");
    }
    else {
      this.year=new_year;
    }
    this.selYear.value=this.year;
  }*/

  }
}
window.customElements.define('pairs-next-operation', PairsNextOperation);
