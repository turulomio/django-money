// Function to use "{0} {1}".format(a, b) style
String.prototype.format = function() {
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
};

function currency_symbol(currency){
    if (currency=='EUR'){
        return '€';
    } 
    else if (currency=='USD'){
        return'$';
    }
}

function currency_string(num, currency){
    num=Math.round(num*100)/100;
    return "{0} {1}".format(num, currency_symbol(currency));
}

//Returns a float with . 
//1.234,56 € => 1234.56
//1,234.56USD => 1234.56
//1,234,567€ => 1234567
//1.234.567 => 1234567
//1,234.567 => 1234.567
//1.234 => 1234 // might be wrong - best guess
//1,234 => 1234 // might be wrong - best guess
//1.2345 => 1.2345
//0,123 => 0.123

function parseNumber(strg){
    var strg = strg || "";
    var decimal = '.';
    strg = strg.replace(/[^0-9$.,]/g, '');
    if(strg.indexOf(',') > strg.indexOf('.')) decimal = ',';
    if((strg.match(new RegExp("\\" + decimal,"g")) || []).length > 1) decimal="";
    if (decimal != "" && (strg.length - strg.indexOf(decimal) - 1 == 3) && strg.indexOf("0" + decimal)!==0) decimal = "";
    strg = strg.replace(new RegExp("[^0-9$" + decimal + "]","g"), "");
    strg = strg.replace(',', '.');
    return parseFloat(strg);
}

