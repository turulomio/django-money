function currency_string(num, currency){
    if (currency=='EUR'){
        var symbol='€';
    } 
    else if (currency=='USD'){
        var symbol='$';
    }
    num=Math.round(num*100)/100;
    return `${num} ${symbol}`;
}