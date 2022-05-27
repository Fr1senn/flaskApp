$('.slider_inner').slick({
    autoplay: true,
    autoplaySpeed: 2000,
    arrows: false,
});



$('.subscription_item form button:button').click(function () {

    let sub = parseFloat($('#sub').val().split(' ')[1]);
    let sub_dur = parseInt($('#sub_dur').val().split(',')[0].split(' ')[0])
    let price = sub * sub_dur;
    if (isNaN(price)) {
        alert('Необходимо авторизоваться!');
    } else {
        alert('Цена: ' + price + ' грн');
    }
});