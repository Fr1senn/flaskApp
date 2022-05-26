$('.slider_inner').slick({
    autoplay: true,
    autoplaySpeed: 2000,
    arrows: false,
});

$('.subscription_item form button:button').click(function () {
    let sub = $('#sub').val().toString().length;
    let sub_dur = $('#sub_dur').val().toString();
    let price = parseInt(sub_dur.split(',')[0].split(' ')[0]) * sub;
    if (isNaN(price)) {
        alert('Необходимо авторизоваться!');
    } else {
        alert('Цена: ' + price + ' грн');
    }
});