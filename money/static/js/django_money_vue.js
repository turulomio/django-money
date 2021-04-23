
export function localtime(value){
    if (value){
        var dateFormat = 'YYYY-MM-DD HH:mm:ss';
        var testDateUtc = moment.utc(value);
        var localDate = testDateUtc.local();
        return (localDate.format(dateFormat)); // 2015-30-01 02:00:00
    }
    console.log("REALLY");
    return null;
}   
