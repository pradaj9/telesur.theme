$(document).ready(function() {
  var urlAjax = $("#more-articles a").attr("href");
  $("#more-articles").append("<img src='++resource++telesur.theme/img/loading.gif' />");
  
  $("#more-articles img").css("display", "none");
  $("#more-articles img").css("margin-bottom", "-6px");
  $("#more-articles a").data("b_start", "8");
  $("#more-articles a").data("limit", "8");
  $("#more-articles a").removeAttr("href");
  $("#more-articles a").click(function(){
        var b_start = parseInt($("#more-articles a").data("b_start"), 10);
        var limit = parseInt($("#more-articles a").data("limit"), 10);
        var kind = "Current";
        if($("#more-articles").hasClass("more-articles-opinion")) {
          kind = "Opinion"
        } else if($("#more-articles").hasClass("more-articles-context")) {
            kind = 'Background'
        } else if($("#more-articles").hasClass("more-articles-interview")) {
                kind = 'Interview'
        }
        $("#more-articles img").css("display", "inline");
        $.ajax({
          url: urlAjax,
           data:{'b_start':b_start, 'kind':kind},
          success: function( data ) {
            $(".article-listing").append(data);
            $("#more-articles a").data("b_start", b_start+limit);
            $("#more-articles img").css("display", "none");
          }
        });
  });
});