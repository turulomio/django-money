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
class ModalWindow extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback(){

    this.template=document.createElement("template");
    this.template.innerHTML=`<style>
body {font-family: Arial, Helvetica, sans-serif;}

/* The Modal (background) */
.modal {
  display: block; /* Hidden none, Modal: block*/
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
#close {
  color: #aaaaaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

#close:hover,
#close:focus {
  color: #000;
  text-decoration: none;
  cursor: pointer;
}
</style>
<!-- The Modal -->
<div id="myModal" class="modal">

  <!-- Modal content -->
  <div class="modal-content">
    <span id="close">&times;</span>
    <div id="innermodal"></div>
  </div>
</div>
`;
        let shadowRoot = this.attachShadow({mode: 'closed'});
        shadowRoot.appendChild(this.template.content.cloneNode(true));
        var innermodal=shadowRoot.querySelector('#innermodal');
        innermodal.innerHTML=this.innerHTML;
        this.span=shadowRoot.querySelector("#close");
        this.modal=shadowRoot.querySelector("#myModal");
        // When the user clicks on <span> (x), close the modal
        var this_=this;
        this.span.onclick = function() {
          this_.modal.style.display = "none";
        }
  }
}
window.customElements.define('modal-window', ModalWindow);
