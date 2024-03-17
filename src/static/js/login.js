// Validation for login form
document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();
    var username = document.getElementById("username").value;
    var password = document.getElementById("pass").value;

    if (username.trim() === "") {
        alert("Please enter your username.");
        return false;
    }

    if (password.trim() === "") {
        alert("Please enter your password.");
        return false;
    }

    // Submit the form if validation passes
    this.submit();
});

// Forgot Password functionality
document.getElementById("forgotPassword").addEventListener("click", function(event) {
    event.preventDefault();
    var username = document.getElementById("username").value;

    if (username.trim() === "") {
        alert("Please enter your username to reset your password.");
        return false;
    }

    // Handle resetting password logic here
    alert("Password reset instructions sent to your email.");
});

document.addEventListener("DOMContentLoaded", function() {
    // Add event listener to the login form submission
    document.getElementById("loginForm").addEventListener("submit", function(event) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // Retrieve the entered username and password
        var username = document.getElementById("username").value;
        var password = document.getElementById("pass").value;

        // Example: Check if username and password are correct (replace with your actual logic)
        if (username === "admin" && password === "nbkr123") {
            // Redirect to a new page
            window.location.href = "/templates/index.html";

            // Show an alert box indicating successful login
            alert("Login successful!");
        } else {
            // Handle unsuccessful login (you can display an error message, etc.)
            alert("Invalid username or password. Please try again.");
        }
    });
});
