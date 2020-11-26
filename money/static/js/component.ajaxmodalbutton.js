// This component is part of the https://github.com/turulomio/reusingcode project
// Make a pull request to this project to update this file

// This component shows a button
// After clicking makes and ajax connection
// parameters:
//   - id. Name of the element 
//   - url. Ajax request url
//   - buttontext. Button text
//   - showbuttonafter. Attribute without value. If missing hides the button after connection
//   - csrf_token
class AjaxModalButton extends HTMLElement {
    constructor() {
      super();
    }
  
    connectedCallback(){



        this.template = document.createElement('template');
        this.template.innerHTML=`
        <style>
  .modal {
    display: none; /* Hidden by default */
    position: fixed; /* Stay in place */
    z-index: 1; /* Sit on top */
    padding-top: 100px; /* Location of the box */
    left: 0;
    top: 0;
    width: 100%; /* Full width */
    height: 100%; /* Full height */
    overflow: auto; /* Enable scroll if needed */
    background-color: rgb(0,0,0); /* Fallback color */
    background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
  }
  
  /* Modal Content */
  .modal-content {
    background-color: #fefefe;
    margin: auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
  }
  
  /* The Close Button */
  .close {
    color: #aaaaaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
  }
  
  .close:hover,
  .close:focus {
    color: #000;
    text-decoration: none;
    cursor: pointer;
  }
  </style>`

  this.appendChild(this.template.content.cloneNode(true));
  //const button = this.shadowRoot.querySelector("button");
  
      if (this.hasAttribute("id")==true){
          this.id=this.getAttribute("id");
      } else{
        this.id="ajax_button";
      }
      
  
      if (this.hasAttribute("url")==true){
        this.url=this.getAttribute("url");
      } else{
        alert("An ajax-button component must have an url attribute");
      }
  
      if (this.hasAttribute("buttontext")==true){
        this.buttontext=this.getAttribute("buttontext");
      } else{
        this.buttontext="Press me";
      }
  
      if (this.hasAttribute("csrf_token")==true){
        this.csrf_token=this.getAttribute("csrf_token");
      } else{
        alert("An ajax-button component must have a csrf_token attribute");
      }
  
      if (this.hasAttribute("showbuttonafter")==false){
        this.showbuttonafter=false;
      } else{
        this.showbuttonafter=true;
      }
  
      this.form=document.createElement("form");
      this.form.setAttribute("method", "post");
      this.appendChild(this.form);
  
      this.button=document.createElement("button");
      this.button_id=this.id+"_button";
      this.button.setAttribute("id", this.button_id);
      this.button.setAttribute("type", "submit");
      this.button.innerHTML=this.buttontext;
      this.form.appendChild(this.button);
  
      this.modal=document.createElement("div");
      this.modal_id=this.id+"_div";
      this.modal.setAttribute("id", this.id+"_div");
      this.modal.setAttribute("class","modal");
      this.appendChild(this.modal);

      // Get the <div> element that holds the modal content
      this.modalcontent = document.createElement("div");
      this.modalcontent.setAttribute("class","modal-content");
      this.modal.appendChild(this.modalcontent);

      // Get the <span> element that closes the modal
      this.span = document.createElement("span");
      this.span.setAttribute("class","close");
      this.span.innerHTML="&times;";
      this.modalcontent.appendChild(this.span);

      this.content = document.createElement("div");
      this.content.setAttribute("id",this.id+"_content");
      this.modal.appendChild(this.content);





// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}


  
        this.button.addEventListener('click', (event) => this.ajax_method(event,this));
        this.span.addEventListener('click', (event) => this.close_modal(event));
        }
  
    close_modal(event){
        modal.style.display = "none";

    }

    //This_ is needed due to scope reasons
    ajax_method(event, this_){
          this.modal.style.display="block";
          event.preventDefault();
          $.ajax({
              type: "POST",
              url: this_.url,
              data: {
                   csrfmiddlewaretoken: this_.csrf_token,
              },
              success: function(result) {
                  $("#"+this_.id+"_content").html(result);
                  if (this_.showbuttonafter==false){
                    $("#"+this_.button_id).hide();
                  }
             },
             error: function(result) {
                  $("#"+this_.div_id).html('<p>"Something is wrong"</p>');
             }
          });
    }
    
   
  }
  window.customElements.define('ajax-modal-button', AjaxModalButton);
  