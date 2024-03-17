function logout() {
    console.log("Logout function called");
    // Show logout successful popup
    alert("Logout successful!");

    // Redirect to login page
    window.location.href = "/templates/login.html";
}

function profile() {
    // Redirect to profile.html page
    window.location.href = "/templates/profile.html";
}

document.addEventListener("DOMContentLoaded", function() {
    var profileButton = document.querySelector("#dropdownMenu a[href='/templates/profile.html']");

    profileButton.addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default link behavior

        // Redirect to profile.html page
        window.location.href = "/templates/profile.html";
    });

    var logoutLinks = document.querySelectorAll("#dropdownMenu a[href='#']");
    logoutLinks.forEach(function(link) {
        link.addEventListener("click", function(event) {
            console.log("Logout option clicked");
            event.preventDefault(); // Prevent default link behavior
            logout(); // Call logout function
        });
    });
});
