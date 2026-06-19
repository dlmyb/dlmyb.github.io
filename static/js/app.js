function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}

$("button.close").on('click', function(event){
    var flag = window.location.pathname + ":" + document.getElementsByTagName('date')[0].textContent;
    document.cookie = "visited=" + flag + ";path=/";
    $("div.news").css("visibility", "hidden");
});

$("div.news").ready(function(){
    var visited = getCookie("visited");
    var flag = window.location.pathname + ":" + document.getElementsByTagName('date')[0].textContent;
    if (visited != flag){
        $("div.news").css("visibility", "visible");
    }
});

feather.replace({'stroke-width': 1});
