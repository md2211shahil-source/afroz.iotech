// ============================================================
// ALZHEIMER VOICE ASSISTANT
// LOGIN + PROFILE JAVASCRIPT
// ============================================================


// ============================================================
// 1. PASSWORD SHOW / HIDE
// ============================================================

const passwordInput =
    document.getElementById("password");

const togglePassword =
    document.getElementById("togglePassword");


if (passwordInput && togglePassword) {

    togglePassword.addEventListener(
        "click",
        function () {

            if (passwordInput.type === "password") {

                passwordInput.type = "text";

                togglePassword.textContent = "🙈";

            } else {

                passwordInput.type = "password";

                togglePassword.textContent = "👁️";

            }

        }
    );
}


// ============================================================
// 2. LOGIN FORM
// ============================================================

const loginForm =
    document.getElementById("loginForm");

const loginMessage =
    document.getElementById("loginMessage");


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const email =
                document
                    .getElementById("email")
                    .value
                    .trim();


            const password =
                document
                    .getElementById("password")
                    .value
                    .trim();


            // =================================================
            // EMPTY VALIDATION
            // =================================================

            if (!email || !password) {

                loginMessage.textContent =
                    "Please enter your email and password.";

                loginMessage.style.color =
                    "#ff7b8a";

                return;
            }


            // =================================================
            // EMAIL VALIDATION
            // =================================================

            const emailPattern =
                /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


            if (!emailPattern.test(email)) {

                loginMessage.textContent =
                    "Please enter a valid email address.";

                loginMessage.style.color =
                    "#ff7b8a";

                return;
            }


            // =================================================
            // PASSWORD VALIDATION
            // =================================================

            if (password.length < 4) {

                loginMessage.textContent =
                    "Password must contain at least 4 characters.";

                loginMessage.style.color =
                    "#ff7b8a";

                return;
            }


            // =================================================
            // SHOW LOGIN PROCESS
            // =================================================

            loginMessage.textContent =
                "Signing in...";

            loginMessage.style.color =
                "#42e0d0";


            // Disable button while request is running

            const loginButton =
                loginForm.querySelector(
                    ".login-button"
                );


            if (loginButton) {

                loginButton.disabled = true;

            }


            // =================================================
            // SEND LOGIN TO FLASK
            // =================================================

            try {

                const formData =
                    new FormData();


                formData.append(
                    "email",
                    email
                );


                formData.append(
                    "password",
                    password
                );


                const response =
                    await fetch(
                        "/login",
                        {
                            method: "POST",
                            body: formData,
                            credentials: "same-origin"
                        }
                    );


                // =================================================
                // CHECK FLASK RESPONSE
                // =================================================

                if (!response.ok) {

                    throw new Error(
                        "Login request failed."
                    );

                }


                // Flask session is now created.

                loginMessage.textContent =
                    "Login successful. Complete your profile...";

                loginMessage.style.color =
                    "#42e0d0";


                // =================================================
                // OPEN PROFILE POPUP
                // =================================================

                setTimeout(function () {

                    openProfileModal();

                }, 500);


            } catch (error) {

                console.error(
                    "Login error:",
                    error
                );


                loginMessage.textContent =
                    "Unable to connect to the server.";

                loginMessage.style.color =
                    "#ff7b8a";


                if (loginButton) {

                    loginButton.disabled = false;

                }

            }

        }
    );
}


// ============================================================
// 3. PROFILE MODAL ELEMENTS
// ============================================================

const profileModal =
    document.getElementById("profileModal");


const profileForm =
    document.getElementById("profileForm");


const profileClose =
    document.getElementById("profileClose");


const profileMessage =
    document.getElementById("profileMessage");


// ============================================================
// 4. OPEN PROFILE MODAL
// ============================================================

function openProfileModal() {

    if (!profileModal) {

        return;

    }


    profileModal.classList.add("show");


    // Focus name field

    const nameInput =
        document.getElementById(
            "profileName"
        );


    if (nameInput) {

        setTimeout(
            function () {

                nameInput.focus();

            },
            300
        );

    }

}


// ============================================================
// 5. CLOSE PROFILE MODAL
// ============================================================

function closeProfileModal() {

    if (!profileModal) {

        return;

    }


    profileModal.classList.remove(
        "show"
    );

}


if (profileClose) {

    profileClose.addEventListener(
        "click",
        function () {

            closeProfileModal();

        }
    );

}


// ============================================================
// 6. CLICK OUTSIDE MODAL TO CLOSE
// ============================================================

if (profileModal) {

    profileModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                profileModal
            ) {

                closeProfileModal();

            }

        }
    );

}


// ============================================================
// 7. PROFILE FORM
// ============================================================

if (profileForm) {

    profileForm.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();


            const name =
                document
                    .getElementById("profileName")
                    .value
                    .trim();


            const mobile =
                document
                    .getElementById("profileMobile")
                    .value
                    .trim();


            const age =
                document
                    .getElementById("profileAge")
                    .value
                    .trim();


            const genderElement =
                document.querySelector(
                    'input[name="gender"]:checked'
                );


            const gender =
                genderElement
                    ? genderElement.value
                    : "";


            // =================================================
            // NAME VALIDATION
            // =================================================

            if (!name) {

                showProfileError(
                    "Please enter your full name."
                );

                return;

            }


            if (name.length < 2) {

                showProfileError(
                    "Please enter a valid name."
                );

                return;

            }


            // =================================================
            // MOBILE VALIDATION
            // =================================================

            const mobilePattern =
                /^[0-9]{10}$/;


            if (!mobilePattern.test(mobile)) {

                showProfileError(
                    "Please enter a valid 10-digit mobile number."
                );

                return;

            }


            // =================================================
            // AGE VALIDATION
            // =================================================

            const ageNumber =
                Number(age);


            if (
                !Number.isInteger(ageNumber) ||
                ageNumber < 1 ||
                ageNumber > 120
            ) {

                showProfileError(
                    "Please enter a valid age."
                );

                return;

            }


            // =================================================
            // GENDER VALIDATION
            // =================================================

            if (!gender) {

                showProfileError(
                    "Please select Male or Female."
                );

                return;

            }


            // =================================================
            // SAVE PROFILE LOCALLY
            // =================================================

            const profile = {

                name: name,

                mobile: mobile,

                age: ageNumber,

                gender: gender

            };


            localStorage.setItem(
                "alzheimerUserProfile",
                JSON.stringify(profile)
            );


            // =================================================
            // SAVE EMAIL LOCALLY
            // =================================================

            const email =
                document
                    .getElementById("email")
                    .value
                    .trim();


            localStorage.setItem(
                "alzheimerUserEmail",
                email
            );


            // =================================================
            // SUCCESS
            // =================================================

            if (profileMessage) {

                profileMessage.textContent =
                    "Profile saved successfully.";

                profileMessage.style.color =
                    "#42e0d0";

            }


            // =================================================
            // GO TO DASHBOARD
            // =================================================

            setTimeout(
                function () {

                    window.location.href =
                        "/dashboard";

                },
                600
            );

        }
    );

}


// ============================================================
// 8. PROFILE ERROR
// ============================================================

function showProfileError(message) {

    if (!profileMessage) {

        return;

    }


    profileMessage.textContent =
        message;


    profileMessage.style.color =
        "#ff7187";

}


// ============================================================
// 9. FORGOT PASSWORD
// ============================================================

const forgotPassword =
    document.getElementById(
        "forgotPassword"
    );


if (forgotPassword) {

    forgotPassword.addEventListener(
        "click",
        function (event) {

            event.preventDefault();


            if (loginMessage) {

                loginMessage.textContent =
                    "Password recovery will be available soon.";

                loginMessage.style.color =
                    "#9b88ff";

            }

        }
    );

}


// ============================================================
// 10. ESC KEY CLOSE MODAL
// ============================================================

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Escape" &&
            profileModal &&
            profileModal.classList.contains("show")
        ) {

            closeProfileModal();

        }

    }
);