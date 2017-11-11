
$(document).ready(function(){  
    $('#sidebar ul li a').each(function(){  
        $this = $(this);
        console.log(window.location.href);
        if(window.location.href.indexOf($this[0].href) ==0 ){
        	console.log($this[0].href);
            console.log(window.location.href);
            $('.current').removeClass('current');
			$(this).parent().removeClass('sub-menu');
			$(this).parent().addClass('current');
        }  
    });
});

$(function(){
    $("#check_all").click(function(){
           $("input[name='checked']").prop("checked",$(this).prop("checked"));
    });
});


//Custom scripts
$(document).ready(function () {

    // Collapse ibox function
    $('.collapse-link').click( function() {
        var ibox = $(this).closest('div.box');
        var button = $(this).find('i');
        var content = ibox.find('div.widget-content');
        content.slideToggle(200);
        button.toggleClass('fa-chevron-up').toggleClass('fa-chevron-down');
        ibox.toggleClass('').toggleClass('border-bottom');
        setTimeout(function () {
            ibox.resize();
            ibox.find('[id^=map-]').resize();
        }, 50);
    });


});

