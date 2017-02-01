$('#registration').on('submit', function(evt) {
    var ageChars = $('#age').val().length;
    var zipcodeChars = $('#zipcode').val().length;
    console.log("IN REGISTRATION")
    if (ageChars < 1) {
        alert('age not entered');
        evt.preventDefault();
    } else if (zipcodeChars != 5) {
        alert('zipcode not valid');
        evt.preventDefault();
    }
});