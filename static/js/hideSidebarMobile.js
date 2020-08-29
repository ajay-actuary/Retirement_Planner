$('.menu-close').on('click', function(){
    if(window.innerWidth >= 767) {
        //mobile
        $('#menuToggle').toggleClass('active');
        $('body').toggleClass('body-push-toright');
        $('#theMenu').toggleClass('menu-open');
    }
});
