let accessToken = null;


async function signup() {

    const username =
        document.getElementById("signup-username").value;

    const email =
        document.getElementById("signup-email").value;

    const password =
        document.getElementById("signup-password").value;


    const response = await fetch("/signup", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            username: username,
            email: email,
            password: password
        })

    });


    const data = await response.json();


    if (response.ok) {

        document.getElementById(
            "signup-message"
        ).innerText = data.message;

    } else {

        document.getElementById(
            "signup-message"
        ).innerText =
            data.detail || "Signup failed";

    }

}


async function login() {

    const username =
        document.getElementById("login-username").value;

    const password =
        document.getElementById("login-password").value;


    const response = await fetch("/login", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            username: username,
            password: password
        })

    });


    const data = await response.json();


    if (response.ok) {

        accessToken = data.access_token;

        document.getElementById(
            "login-message"
        ).innerText = "Login successful";

    } else {

        document.getElementById(
            "login-message"
        ).innerText =
            data.detail || "Login failed";

    }

}


async function generateEvents() {

    if (!accessToken) {

        document.getElementById(
            "generate-message"
        ).innerText =
            "Please login first.";

        return;

    }


    const count =
        parseInt(
            document.getElementById(
                "event-count"
            ).value
        );


    const response = await fetch("/generate", {

        method: "POST",

        headers: {

            "Content-Type": "application/json",

            "Authorization":
                `Bearer ${accessToken}`

        },

        body: JSON.stringify({
            count: count
        })

    });


    const data = await response.json();


    if (response.ok) {

        document.getElementById(
            "generate-message"
        ).innerText =
            `${data.events_generated} events generated successfully`;

    } else {

        document.getElementById(
            "generate-message"
        ).innerText =
            data.detail || "Event generation failed";

    }

}