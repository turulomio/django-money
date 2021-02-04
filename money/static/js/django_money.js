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
    } else {
            return "???";
    }
}

function my_round(num, decimals = 2) {
    return Math.round(num*Math.pow(10, decimals))/Math.pow(10, decimals);
}

function currency_string(num, currency, decimals=2){
    return "{0} {1}".format(my_round(num,decimals).toString(), currency_symbol(currency));
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
    strg = strg.toString().replace(',', '.');
    return parseFloat(strg);
}

// Function used in several project pages. Adding or updating strategies
function strategy_update_labels(cmbType){
    var additional1 = $('label[for="id_additional1"]');
    var additional2 = $('label[for="id_additional2"]');
    var additional3 = $('label[for="id_additional3"]');
    var additional4 = $('label[for="id_additional4"]');
    var additional5 = $('label[for="id_additional5"]');
    var additional6 = $('label[for="id_additional6"]');
    var additional7 = $('label[for="id_additional7"]');
    var additional8 = $('label[for="id_additional8"]');
    var additional9 = $('label[for="id_additional9"]');
    var additional10 = $('label[for="id_additional10"]');
    if (cmbType.selectedIndex=="0"){//Generic
        additional1.html(gettext("Additional 1"));
        additional2.html(gettext("Additional 2"));
        additional3.html(gettext("Additional 3"));
        additional4.html(gettext("Additional 4"));
        additional5.html(gettext("Additional 5"));
        additional6.html(gettext("Additional 6"));
        additional7.html(gettext("Additional 7"));
        additional8.html(gettext("Additional 8"));
        additional9.html(gettext("Additional 9"));
        additional10.html(gettext("Additional 10"));
        additional1.parent().parent().show();
        additional2.parent().parent().show();
        additional3.parent().parent().show();
        additional4.parent().parent().show();
        additional5.parent().parent().show();
        additional6.parent().parent().show();
        additional7.parent().parent().show();
        additional8.parent().parent().show();
        additional9.parent().parent().show();
        additional10.parent().parent().show();
    } else if (cmbType.selectedIndex=="1"){//Generic
        additional1.parent().parent().hide();
        additional2.parent().parent().hide();
        additional3.parent().parent().hide();
        additional4.parent().parent().hide();
        additional5.parent().parent().hide();
        additional6.parent().parent().hide();
        additional7.parent().parent().hide();
        additional8.parent().parent().hide();
        additional9.parent().parent().hide();
        additional10.parent().parent().hide();
    } else if (cmbType.selectedIndex=="2"){//Pairs in same account
        additional1.html(gettext("Worse product"));
        additional2.html(gettext("Best product"));
        additional3.html(gettext("Account"));
        additional1.parent().parent().show();
        additional2.parent().parent().show();
        additional3.parent().parent().show();
        additional4.parent().parent().hide();
        additional5.parent().parent().hide();
        additional6.parent().parent().hide();
        additional7.parent().parent().hide();
        additional8.parent().parent().hide();
        additional9.parent().parent().hide();
        additional10.parent().parent().hide();
    } else if (cmbType.selectedIndex=="3"){//Product ranges
        additional1.html(gettext("Product"));
        additional2.html(gettext("Percentage between ranges x1000"));
        additional3.html(gettext("Percentage gains x1000"));
        additional4.html(gettext("Amount"));
        additional5.html(gettext("Recomendation method"));
        additional6.html(gettext("Only first"));
        additional7.html(gettext("Account"));
        additional1.parent().parent().show();
        additional2.parent().parent().show();
        additional3.parent().parent().show();
        additional4.parent().parent().show();
        additional5.parent().parent().show();
        additional6.parent().parent().show();
        additional7.parent().parent().show();
        additional8.parent().parent().hide();
        additional9.parent().parent().hide();
        additional10.parent().parent().hide();
    }
    
}
