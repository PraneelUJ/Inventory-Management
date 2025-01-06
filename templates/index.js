// function onSignIn(googleUser) {
//     var profile = googleUser.getBasicProfile();
//     $("#name").text(profile.getName());
//     $("#email").text(profile.getEmail());
//     $("#image").attr('src', profile.getImageUrl());
//     $(".data").css("display", "block");
//     $(".g-signin2").css("display", "none");

//     // Get the ID token and send it to the Flask backend
//     var id_token = googleUser.getAuthResponse().id_token;
//     $.ajax({
//         url: "/google-login",
//         method: "POST",
//         contentType: "application/json",
//         data: JSON.stringify({ id_token: id_token }),
//         success: function(response) {
//             console.log("Logged in successfully:", response);
//         },
//         error: function(error) {
//             console.log("Error during login:", error);
//         }
//     });
// }

// function signOut() {
//     var auth2 = gapi.auth2.getAuthInstance();
//     auth2.signOut().then(function () {
//         alert("You have been signed out successfully");
//         $(".g-signin2").css("display", "block");
//         $(".data").css("display", "none");
//     });
// }
