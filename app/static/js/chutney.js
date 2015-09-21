$(document).ready(function () {
    $('.category-link').click(function (e) {
        e.preventDefault();

        var target = $($(this).attr('href'));

        $('html, body').animate({
            scrollTop: target.offset().top - $('.top-bar').height()
        }, 300, 'swing');
    });
});