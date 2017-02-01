$('.user-info').on('submit', function(evt) {
    // evt.preventDefault();
    var userChars = $('#username').val();
    console.log('userChars: ' +userChars);
    var passChars = $('#password').val().length;
    if ((/(.+)@(.+\.){1,}(com|net|gov|edu)/g).test(userChars) === false) {
        evt.preventDefault();
        // flash("please enter a valid email");
        alert('username not email');
        // $.get('/register', "error: 'username not email'")
    }
    else if (passChars < 2) {
        // flash('please enter a password');
        alert('password not entered');
        evt.preventDefault();
    }

});

