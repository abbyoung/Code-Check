$(document).ready(function(){

});

var submitBookmarklet = $(document.getElementsByTagName('html'));

submitBookmarklet.on("click", function(event){
    $.ajax({
        url: "http://localhost:5000/results/",
        method: "POST",
        data: $(submitBookmarklet).serialize(),

    }).done(function(data){
        alert(data);
    }).fail(function(){
        alert('fail!!!');
    });

});
