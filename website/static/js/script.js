$('.slider_inner').slick({
    autoplay: true,
    autoplaySpeed: 2000,
    arrows: false,
});

$('.subscription_item form button:button').click(function () {
    sub = $('#sub').val().toString().length;
    sub_dur = $('#sub_dur').val().toString()
    alert('Цена: ' + parseInt(sub_dur.split(',')[0].split(' ')[0]) * sub + ' грн');
});