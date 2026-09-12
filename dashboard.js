document.addEventListener("DOMContentLoaded", () => {

    // =========================================================
    // ALZHEIMER VOICE ASSISTANT
    // PROFESSIONAL DASHBOARD JAVASCRIPT
    // =========================================================


    // =========================================================
    // USER PROFILE
    // =========================================================

    const savedProfile =
        localStorage.getItem("alzheimerUserProfile");

    if (savedProfile) {

        try {

            const profile =
                JSON.parse(savedProfile);

            const dashboardUserName =
                document.getElementById(
                    "dashboardUserName"
                );

            const sidebarUserName =
                document.getElementById(
                    "sidebarUserName"
                );

            const userAvatar =
                document.getElementById(
                    "userAvatar"
                );


            if (profile.name) {

                if (dashboardUserName) {

                    dashboardUserName.textContent =
                        profile.name;
                }


                if (sidebarUserName) {

                    sidebarUserName.textContent =
                        profile.name;
                }


                if (userAvatar) {

                    userAvatar.textContent =
                        profile.name
                            .charAt(0)
                            .toUpperCase();
                }

            }

        } catch (error) {

            console.log(
                "Profile error:",
                error
            );

        }

    }


    // =========================================================
    // SIDEBAR 3-DOT TOGGLE
    // =========================================================

    const sidebar =
        document.querySelector(".sidebar");


    const app =
        document.querySelector(".app");


    if (sidebar && app) {

        // -----------------------------------------------------
        // Create 3-dot button
        // -----------------------------------------------------

        const sidebarToggle =
            document.createElement("button");


        sidebarToggle.type =
            "button";


        sidebarToggle.className =
            "sidebar-toggle";


        sidebarToggle.id =
            "sidebarToggle";


        sidebarToggle.setAttribute(
            "aria-label",
            "Open navigation menu"
        );


        sidebarToggle.setAttribute(
            "title",
            "Navigation menu"
        );


        sidebarToggle.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;


        document.body.appendChild(
            sidebarToggle
        );


        // -----------------------------------------------------
        // Overlay
        // -----------------------------------------------------

        const sidebarOverlay =
            document.createElement("div");


        sidebarOverlay.className =
            "sidebar-overlay";


        sidebarOverlay.id =
            "sidebarOverlay";


        document.body.appendChild(
            sidebarOverlay
        );


        // -----------------------------------------------------
        // Toggle sidebar
        // -----------------------------------------------------

        function toggleSidebar() {

            sidebar.classList.toggle(
                "sidebar-open"
            );


            sidebarOverlay.classList.toggle(
                "active"
            );


            // Keep hamburger icon unchanged
sidebarToggle.classList.remove("active");

        }


        sidebarToggle.addEventListener(
            "click",
            toggleSidebar
        );


        sidebarOverlay.addEventListener(
            "click",
            toggleSidebar
        );


        // -----------------------------------------------------
        // Close sidebar when navigation item clicked
        // -----------------------------------------------------

        const navigationItems =
            sidebar.querySelectorAll(
                ".nav-item"
            );


        navigationItems.forEach(
            item => {

                item.addEventListener(
                    "click",
                    () => {

                        if (
                            window.innerWidth <= 900
                        ) {

                            sidebar.classList.remove(
                                "sidebar-open"
                            );


                            sidebarOverlay.classList.remove(
                                "active"
                            );


                            sidebarToggle.classList.remove(
                                "active"
                            );

                        }

                    }
                );

            }
        );


        // -----------------------------------------------------
        // Escape key closes sidebar
        // -----------------------------------------------------

        document.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Escape"
                ) {

                    sidebar.classList.remove(
                        "sidebar-open"
                    );


                    sidebarOverlay.classList.remove(
                        "active"
                    );


                    sidebarToggle.classList.remove(
                        "active"
                    );

                }

            }
        );

    }


    // =========================================================
    // DATE & TIME
    // =========================================================

    function updateDateTime() {

        const now =
            new Date();


        const dateElement =
            document.getElementById(
                "todayDate"
            );


        const dayElement =
            document.getElementById(
                "todayDay"
            );


        const timeElement =
            document.getElementById(
                "currentTime"
            );


        if (dateElement) {

            dateElement.textContent =
                now.toLocaleDateString(
                    "en-IN",
                    {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                    }
                );

        }


        if (dayElement) {

            dayElement.textContent =
                now.toLocaleDateString(
                    "en-IN",
                    {
                        weekday: "long"
                    }
                );

        }


        if (timeElement) {

            timeElement.textContent =
                now.toLocaleTimeString(
                    "en-IN",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit"
                    }
                );

        }

    }


    updateDateTime();


    setInterval(
        updateDateTime,
        1000
    );


    // =========================================================
    // LOAD REMINDERS
    // =========================================================

    let remindersLoadedOnce =
        false;


    async function loadReminders() {

        const scheduleList =
            document.getElementById(
                "scheduleList"
            );


        if (
            !remindersLoadedOnce &&
            scheduleList
        ) {

            scheduleList.innerHTML = `
                <div class="schedule-empty">
                    Loading reminders...
                    <br>
                    <small>Please wait</small>
                </div>
            `;

        }


        try {

            const response =
                await fetch(
                    "/api/reminders",
                    {
                        method: "GET",
                        credentials: "same-origin",
                        cache: "no-store"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Server returned HTTP " +
                    response.status
                );

            }


            const data =
                await response.json();


            console.log(
                "Reminders API response:",
                data
            );


            if (
                !data ||
                data.success !== true ||
                !Array.isArray(
                    data.reminders
                )
            ) {

                throw new Error(
                    "Invalid reminder data received."
                );

            }


            const reminders =
                data.reminders;


            remindersLoadedOnce =
                true;


            displayReminders(
                reminders
            );


            updateTaskCount(
                reminders
            );


            updateNextReminder(
                reminders
            );


        } catch (error) {

            console.error(
                "Reminder loading error:",
                error
            );


            if (
                !remindersLoadedOnce &&
                scheduleList
            ) {

                scheduleList.innerHTML = `
                    <div class="schedule-empty">
                        Unable to load reminders.
                        <br>
                        <small>
                            Please refresh the page.
                        </small>
                    </div>
                `;

            }

        }

    }


    // =========================================================
    // DISPLAY REMINDERS
    // =========================================================

    function displayReminders(
        reminders
    ) {

        const scheduleList =
            document.getElementById(
                "scheduleList"
            );


        if (!scheduleList) {

            return;

        }


        scheduleList.innerHTML =
            "";


        if (
            !reminders ||
            reminders.length === 0
        ) {

            scheduleList.innerHTML = `
                <div class="schedule-empty">
                    No reminders scheduled yet.
                </div>
            `;

            return;

        }


        reminders.forEach(
            reminder => {

                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "schedule-item";


                const completed =
                    Number(
                        reminder.completed
                    ) === 1;


                const icon =
                    getReminderIcon(
                        reminder.reminder_text
                    );


                item.innerHTML = `

                    <div class="task-icon">
                        ${icon}
                    </div>


                    <div class="task-info">

                        <strong>
                            ${escapeHTML(
                                reminder.reminder_text
                            )}
                        </strong>


                        <small>
                            ${escapeHTML(
                                formatDate(
                                    reminder.reminder_date
                                )
                            )}
                        </small>

                    </div>


                    <div class="task-time">

                        ${escapeHTML(
                            formatTime(
                                reminder.reminder_time
                            )
                        )}


                        <span class="badge ${
                            completed
                                ? "completed"
                                : "upcoming"
                        }">

                            ${
                                completed
                                    ? "Completed ✓"
                                    : "Upcoming"
                            }

                        </span>

                    </div>


                    <button
                        class="delete-reminder-button"
                        data-id="${reminder.id}"
                        title="Delete Reminder"
                        type="button"
                        aria-label="Delete Reminder"
                    >

                        <svg
                            class="delete-icon"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >

                            <path
                                d="M3 6h18"
                            ></path>

                            <path
                                d="M8 6V4h8v2"
                            ></path>

                            <path
                                d="M19 6l-1 15H6L5 6"
                            ></path>

                            <path
                                d="M10 11v6"
                            ></path>

                            <path
                                d="M14 11v6"
                            ></path>

                        </svg>

                    </button>

                `;


                scheduleList.appendChild(
                    item
                );

            }
        );


        // =====================================================
        // DELETE BUTTON EVENTS
        // =====================================================

        const deleteButtons =
            document.querySelectorAll(
                ".delete-reminder-button"
            );


        deleteButtons.forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        const reminderId =
                            button.dataset.id;


                        deleteReminder(
                            reminderId
                        );

                    }
                );

            }
        );

    }


    // =========================================================
    // FORMAT DATE
    // =========================================================

    function formatDate(
        date
    ) {

        if (!date) {

            return "Today";

        }


        const value =
            String(date);


        const parts =
            value.split("-");


        if (
            parts.length === 3
        ) {

            const year =
                Number(
                    parts[0]
                );


            const month =
                Number(
                    parts[1]
                );


            const day =
                Number(
                    parts[2]
                );


            if (
                !Number.isNaN(year) &&
                !Number.isNaN(month) &&
                !Number.isNaN(day)
            ) {

                const dateObject =
                    new Date(
                        year,
                        month - 1,
                        day
                    );


                return dateObject.toLocaleDateString(
                    "en-IN",
                    {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                    }
                );

            }

        }


        return value;

    }


    // =========================================================
    // DELETE REMINDER
    // =========================================================

    async function deleteReminder(
        reminderId
    ) {

        const confirmed =
            confirm(
                "Are you sure you want to delete this reminder?"
            );


        if (!confirmed) {

            return;

        }


        try {

            const response =
                await fetch(
                    `/api/delete-reminder/${reminderId}`,
                    {
                        method: "DELETE",
                        credentials: "same-origin"
                    }
                );


            const result =
                await response.json();


            if (
                !response.ok ||
                !result.success
            ) {

                alert(
                    result.message ||
                    "Reminder could not be deleted."
                );

                return;

            }


            const aiMessage =
                document.getElementById(
                    "aiMessage"
                );


            if (aiMessage) {

                aiMessage.textContent =
                    "Reminder deleted successfully.";

            }


            await loadReminders();


        } catch (error) {

            console.error(
                "Delete reminder error:",
                error
            );


            alert(
                "Server error. Reminder could not be deleted."
            );

        }

    }


    // =========================================================
    // REMINDER ICON
    // =========================================================

    function getReminderIcon(
        text
    ) {

        const value =
            String(
                text || ""
            ).toLowerCase();


        if (
            value.includes("medicine") ||
            value.includes("dawa") ||
            value.includes("tablet") ||
            value.includes("pill") ||
            value.includes("medic")
        ) {

            return "💊";

        }


        if (
            value.includes("doctor") ||
            value.includes("hospital") ||
            value.includes("appointment")
        ) {

            return "🩺";

        }


        if (
            value.includes("walk") ||
            value.includes("walking") ||
            value.includes("exercise")
        ) {

            return "🚶";

        }


        if (
            value.includes("eat") ||
            value.includes("food") ||
            value.includes("breakfast") ||
            value.includes("lunch") ||
            value.includes("dinner") ||
            value.includes("khana")
        ) {

            return "🍽️";

        }


        if (
            value.includes("water") ||
            value.includes("paani")
        ) {

            return "💧";

        }


        return "🔔";

    }


    // =========================================================
    // FORMAT TIME
    // =========================================================

    function formatTime(
        time
    ) {

        if (!time) {

            return "--:--";

        }


        const parts =
            String(time).split(":");


        if (
            parts.length < 2
        ) {

            return time;

        }


        let hour =
            parseInt(
                parts[0],
                10
            );


        const minute =
            parts[1];


        if (
            Number.isNaN(hour)
        ) {

            return time;

        }


        const ampm =
            hour >= 12
                ? "PM"
                : "AM";


        hour =
            hour % 12;


        if (
            hour === 0
        ) {

            hour = 12;

        }


        return `${hour}:${minute} ${ampm}`;

    }


    // =========================================================
    // TASK COUNT
    // =========================================================

    function updateTaskCount(
        reminders
    ) {

        const taskCount =
            document.getElementById(
                "taskCount"
            );


        if (!taskCount) {

            return;

        }


        taskCount.textContent =
            reminders.length;

    }


    // =========================================================
    // NEXT REMINDER
    // =========================================================

    function updateNextReminder(
        reminders
    ) {

        const nextReminder =
            document.getElementById(
                "nextReminder"
            );


        const nextReminderTime =
            document.getElementById(
                "nextReminderTime"
            );


        if (
            !nextReminder ||
            !nextReminderTime
        ) {

            return;

        }


        const pending =
            reminders
                .filter(
                    reminder =>
                        Number(
                            reminder.completed
                        ) !== 1
                )
                .sort(
                    (a, b) => {

                        const dateA =
                            String(
                                a.reminder_date ||
                                ""
                            );


                        const dateB =
                            String(
                                b.reminder_date ||
                                ""
                            );


                        const timeA =
                            String(
                                a.reminder_time ||
                                ""
                            );


                        const timeB =
                            String(
                                b.reminder_time ||
                                ""
                            );


                        return (
                            `${dateA} ${timeA}`
                                .localeCompare(
                                    `${dateB} ${timeB}`
                                )
                        );

                    }
                );


        if (
            pending.length === 0
        ) {

            nextReminder.textContent =
                "No reminder";


            nextReminderTime.textContent =
                "--:--";


            return;

        }


        const next =
            pending[0];


        nextReminder.textContent =
            next.reminder_text;


        nextReminderTime.textContent =
            formatTime(
                next.reminder_time
            );

    }


    // =========================================================
    // ESCAPE HTML
    // =========================================================

    function escapeHTML(
        value
    ) {

        const div =
            document.createElement(
                "div"
            );


        div.textContent =
            value == null
                ? ""
                : String(value);


        return div.innerHTML;

    }


    // =========================================================
    // VOICE MODE
    // =========================================================

    const voiceModeToggle =
        document.getElementById(
            "voiceModeToggle"
        );


    const voicePanel =
        document.getElementById(
            "voicePanel"
        );


    const voiceStatus =
        document.getElementById(
            "voiceStatus"
        );


    const voiceModeText =
        document.getElementById(
            "voiceModeText"
        );


    let voiceMode =
        true;


    if (voiceModeToggle) {

        voiceModeToggle.addEventListener(
            "click",
            () => {

                voiceMode =
                    !voiceMode;


                voiceModeToggle.classList.toggle(
                    "active",
                    voiceMode
                );


                if (voicePanel) {

                    voicePanel.classList.toggle(
                        "voice-disabled",
                        !voiceMode
                    );

                }


                if (voiceStatus) {

                    voiceStatus.textContent =
                        voiceMode
                            ? "Listening is ready"
                            : "Voice Mode is OFF";

                }


                if (voiceModeText) {

                    voiceModeText.textContent =
                        voiceMode
                            ? "Voice Mode ON"
                            : "Voice Mode OFF";

                }

            }
        );

    }


    // =========================================================
    // TEXT REMINDER
    // =========================================================

    const reminderInput =
        document.getElementById(
            "reminderInput"
        );


    const sendReminderButton =
        document.getElementById(
            "sendReminderButton"
        );


    const aiMessage =
        document.getElementById(
            "aiMessage"
        );


    const playerMessage =
        document.getElementById(
            "playerMessage"
        );


    const playerStatus =
        document.getElementById(
            "playerStatus"
        );


    async function sendReminder() {

        const text =
            reminderInput
                ? reminderInput.value.trim()
                : "";


        if (!text) {

            if (aiMessage) {

                aiMessage.textContent =
                    "Please type a reminder first.";

            }

            return;

        }


        if (aiMessage) {

            aiMessage.textContent =
                "AI is checking your reminder...";

        }


        if (playerMessage) {

            playerMessage.textContent =
                "Processing reminder...";

        }


        if (playerStatus) {

            playerStatus.textContent =
                "Processing";

        }


        try {

            const response =
                await fetch(
                    "/api/add-reminder",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        credentials:
                            "same-origin",

                        body:
                            JSON.stringify({
                                user_text:
                                    text
                            })

                    }
                );


            const result =
                await response.json();


            if (
                !response.ok ||
                !result.success
            ) {

                const message =
                    result.message ||
                    "This reminder could not be saved.";


                if (aiMessage) {

                    aiMessage.textContent =
                        message;

                }


                if (playerMessage) {

                    playerMessage.textContent =
                        message;

                }


                if (playerStatus) {

                    playerStatus.textContent =
                        "Not Saved";

                }


                return;

            }


            // =================================================
            // SUCCESS
            // =================================================

            if (aiMessage) {

                aiMessage.textContent =
                    "Reminder saved successfully.";

            }


            if (playerMessage) {

                playerMessage.textContent =
                    `Saved: ${
                        result.reminder.reminder_text
                    }`;

            }


            if (playerStatus) {

                playerStatus.textContent =
                    "Saved";

            }


            if (reminderInput) {

                reminderInput.value =
                    "";

            }


            await loadReminders();


        } catch (error) {

            console.error(
                "Add reminder error:",
                error
            );


            if (aiMessage) {

                aiMessage.textContent =
                    "Unable to connect to the server.";

            }


            if (playerMessage) {

                playerMessage.textContent =
                    "Server connection error.";

            }


            if (playerStatus) {

                playerStatus.textContent =
                    "Error";

            }

        }

    }


    if (sendReminderButton) {

        sendReminderButton.addEventListener(
            "click",
            sendReminder
        );

    }


    // =========================================================
    // ENTER KEY
    // =========================================================

    if (reminderInput) {

        reminderInput.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    sendReminder();

                }

            }
        );

    }


    // =========================================================
    // VOICE BUTTON
    // =========================================================

    const voiceButton =
        document.getElementById(
            "voiceButton"
        );


    if (voiceButton) {

        voiceButton.addEventListener(
            "click",
            async () => {

                // ---------------------------------------------
                // CHECK VOICE MODE
                // ---------------------------------------------

                if (!voiceMode) {

                    if (aiMessage) {

                        aiMessage.textContent =
                            "Please turn Voice Mode ON first.";

                    }

                    return;

                }


                // ---------------------------------------------
                // START RECORDING
                // ---------------------------------------------

                voiceButton.disabled =
                    true;


                voiceButton.style.transform =
                    "scale(1.08)";


                if (voiceStatus) {

                    voiceStatus.textContent =
                        "🎤 Listening... Please speak clearly.";

                }


                if (aiMessage) {

                    aiMessage.textContent =
                        "Listening to your reminder...";

                }


                if (playerMessage) {

                    playerMessage.textContent =
                        "Recording your voice...";

                }


                if (playerStatus) {

                    playerStatus.textContent =
                        "Listening";

                }


                try {

                    const response =
                        await fetch(
                            "/api/voice-reminder",
                            {
                                method: "POST",
                                credentials:
                                    "same-origin"
                            }
                        );


                    const result =
                        await response.json();


                    // -----------------------------------------
                    // FAILED
                    // -----------------------------------------

                    if (
                        !response.ok ||
                        !result.success
                    ) {

                        const message =
                            result.message ||
                            "Voice reminder could not be saved.";


                        if (voiceStatus) {

                            voiceStatus.textContent =
                                "Ready to listen";

                        }


                        if (aiMessage) {

                            aiMessage.textContent =
                                message;

                        }


                        if (playerMessage) {

                            playerMessage.textContent =
                                result.recognized_text
                                    ? `I heard: "${result.recognized_text}"`
                                    : message;

                        }


                        if (playerStatus) {

                            playerStatus.textContent =
                                "Not Saved";

                        }


                        return;

                    }


                    // -----------------------------------------
                    // SUCCESS
                    // -----------------------------------------

                    if (voiceStatus) {

                        voiceStatus.textContent =
                            "✅ Reminder saved successfully.";

                    }


                    if (aiMessage) {

                        aiMessage.textContent =
                            `Reminder saved: ${
                                result.reminder.reminder_text
                            }`;

                    }


                    if (playerMessage) {

                        playerMessage.textContent =
                            result.recognized_text
                                ? `Voice: "${result.recognized_text}"`
                                : "Voice reminder saved.";

                    }


                    if (playerStatus) {

                        playerStatus.textContent =
                            "Saved";

                    }


                    await loadReminders();


                } catch (error) {

                    console.error(
                        "Voice reminder error:",
                        error
                    );


                    if (voiceStatus) {

                        voiceStatus.textContent =
                            "Voice connection error.";

                    }


                    if (aiMessage) {

                        aiMessage.textContent =
                            "Unable to connect to voice assistant.";

                    }


                    if (playerStatus) {

                        playerStatus.textContent =
                            "Error";

                    }


                } finally {

                    voiceButton.disabled =
                        false;


                    voiceButton.style.transform =
                        "";

                }

            }
        );

    }


    // =========================================================
    // QUICK ACTIONS
    // =========================================================

    const addReminderButton =
        document.getElementById(
            "addReminderButton"
        );


    if (addReminderButton) {

        addReminderButton.addEventListener(
            "click",
            () => {

                if (reminderInput) {

                    reminderInput.focus();

                }

            }
        );

    }


    const voiceNoteButton =
        document.getElementById(
            "voiceNoteButton"
        );


    if (voiceNoteButton) {

        voiceNoteButton.addEventListener(
            "click",
            () => {

                if (aiMessage) {

                    aiMessage.textContent =
                        "Voice Note feature will be connected next.";

                }

            }
        );

    }


    const emergencyButton =
        document.getElementById(
            "emergencyButton"
        );


    if (emergencyButton) {

        emergencyButton.addEventListener(
            "click",
            () => {

                alert(
                    "Emergency feature will be configured later."
                );

            }
        );

    }


    const familyButton =
        document.getElementById(
            "familyButton"
        );


    if (familyButton) {

        familyButton.addEventListener(
            "click",
            () => {

                alert(
                    "Family contact feature will be configured later."
                );

            }
        );

    }


    const reportButton =
        document.getElementById(
            "reportButton"
        );


    if (reportButton) {

        reportButton.addEventListener(
            "click",
            () => {

                alert(
                    "Report feature will be configured later."
                );

            }
        );

    }


    // =========================================================
    // LOGOUT
    // =========================================================

    const logoutButton =
        document.getElementById(
            "logoutButton"
        );


    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            () => {

                localStorage.removeItem(
                    "alzheimerUserProfile"
                );


                localStorage.removeItem(
                    "alzheimerUserEmail"
                );


                window.location.href =
                    "/logout";

            }
        );

    }


   // =========================================================
// SIDEBAR MENU
// =========================================================

const sidebarToggle =
    document.getElementById("sidebarToggle");

const sidebarOverlay =
    document.getElementById("sidebarOverlay");


if (sidebarToggle) {

    sidebarToggle.addEventListener(
        "click",
        (event) => {

            event.preventDefault();

            event.stopPropagation();

            document.body.classList.toggle(
                "sidebar-open"
            );

        }
    );
}


if (sidebarOverlay) {

    sidebarOverlay.addEventListener(
        "click",
        () => {

            document.body.classList.remove(
                "sidebar-open"
            );

        }
    );
}


// =========================================================
// CLOSE SIDEBAR AFTER MENU ITEM CLICK
// =========================================================

document.querySelectorAll(
    ".nav-item"
).forEach(
    item => {

        item.addEventListener(
            "click",
            () => {

                if (
                    window.innerWidth <= 900
                ) {

                    document.body.classList.remove(
                        "sidebar-open"
                    );

                }

            }
        );

    }
);


// =========================================================
// INITIAL LOAD
// =========================================================

loadReminders();


// =========================================================
// BACKGROUND REFRESH
// =========================================================

setInterval(
    loadReminders,
    10000
);

});