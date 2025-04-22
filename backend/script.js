document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault();
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirect user based on role
            if (data.role === "admin") {
                window.location.href = "admin_dashboard.html";
            } else {
                window.location.href = "user_dashboard.html";
            }
        } else {
            const errorDiv = document.getElementById("loginError");
            errorDiv.style.display = "block";
            errorDiv.innerText = "Invalid username or password!";
        }
    })
    .catch(error => console.error("Error:", error));
});
