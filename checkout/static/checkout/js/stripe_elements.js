
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: '#000',
        fontFamily: 'Courier New',
        fontSmoothing: 'antialiased',
        borderColor: 'red',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

var card = elements.create('card');
card.mount('#card-element', { style: style });

// Handle real-time validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        errorDiv.textContent = event.error.message;
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    card.update({ 'disabled': true });
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    }).then(function (result) {
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            errorDiv.textContent = result.error.message;
            card.update({ 'disabled': false });
            $('#submit-button').attr('disabled', false);
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
                console.log('Payment succeeded');
            }
        }
    });
});
