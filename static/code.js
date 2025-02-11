window.onload= function(){
    user_id= document.getElementById('user_id').innerHTML;
    var owned= document.getElementsByClassName(user_id);
    console.log(owned);
    for(var i=0; i< owned.length; i++){
        owned[i].setAttribute("style","visibility: visible")
    }
};
