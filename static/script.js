(() => {
    "use strict";

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const supportsFinePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

    const dom = {
        body: document.body,
        root: document.documentElement,
        skipLink: document.querySelector(".skip-link"),
        starField: document.getElementById("starField"),
        themeToggle: document.getElementById("themeToggle"),
        themeColor: document.querySelector('meta[name="theme-color"]'),
        systemStatus: document.getElementById("systemStatus"),
        statusText: document.getElementById("statusText"),
        plannerForm: document.getElementById("plannerForm"),
        plannerSection: document.getElementById("planner"),
        plannerShell: document.querySelector(".planner-shell"),
        submitButton: document.getElementById("submitButton"),
        submitLabel: document.querySelector(".submit-label"),
        loadingPanel: document.getElementById("loadingPanel"),
        loadingTitle: document.getElementById("loadingTitle"),
        loadingDescription: document.getElementById("loadingDescription"),
        loadingBar: document.getElementById("loadingBar"),
        loadingSteps: Array.from(document.querySelectorAll(".loading-steps span")),
        progressRing: document.getElementById("progressRing"),
        progressValue: document.getElementById("progressValue"),
        resultSection: document.getElementById("resultSection"),
        resultHeading: document.getElementById("resultHeading"),
        resultAnnouncement: document.getElementById("resultAnnouncement"),
        resultSubtitle: document.getElementById("resultSubtitle"),
        resultMeta: document.getElementById("resultMeta"),
        resultContent: document.getElementById("resultContent"),
        copyButton: document.getElementById("copyButton"),
        downloadButton: document.getElementById("downloadButton"),
        newPlanButton: document.getElementById("newPlanButton"),
        toast: document.getElementById("toast"),
        toastMessage: document.getElementById("toastMessage"),
        toastIcon: document.querySelector(".toast-icon"),
        constraintCount: document.getElementById("constraintCount"),
        interests: document.getElementById("interests"),
        constraints: document.getElementById("constraints"),
        choiceChips: Array.from(document.querySelectorAll(".choice-chip")),
        viewDemoButton: document.getElementById("viewDemoButton"),
        demoSection: document.getElementById("demoSection"),
        demoHeading: document.getElementById("demoHeading"),
        demoClose: document.getElementById("demoClose"),
        summaryLocation: document.getElementById("summaryLocation"),
        summaryBudget: document.getElementById("summaryBudget"),
        summaryGroup: document.getElementById("summaryGroup"),
        summaryWeather: document.getElementById("summaryWeather"),
    };

    const fields = {
        location: document.getElementById("location"),
        interests: document.getElementById("interests"),
        budget: document.getElementById("budget"),
        group_size: document.getElementById("groupSize"),
        available_time: document.getElementById("availableTime"),
        weather: document.getElementById("weather"),
        transport: document.getElementById("transport"),
        constraints: document.getElementById("constraints"),
    };

    const state = {
        currentPlan: "",
        currentMeta: null,
        isSubmitting: false,
        toastTimer: null,
        pointerFrame: null,
        configReady: null,
        health: null,
        demoReturnFocus: null,
    };

    const icons = {
        location: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s6-5.2 6-11a6 6 0 1 0-12 0c0 5.8 6 11 6 11Z"/><circle cx="12" cy="10" r="2"/></svg>',
        budget: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="6" width="18" height="13" rx="3"/><path d="M16 11h5"/></svg>',
        group: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8" r="3"/><path d="M3.5 20v-2.2A4.8 4.8 0 0 1 8.3 13h1.4a4.8 4.8 0 0 1 4.8 4.8V20M16 5.5a3 3 0 0 1 0 5.8M17.5 13a4.5 4.5 0 0 1 3 4.3V20"/></svg>',
        success: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>',
        error: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 17h.01"/></svg>',
    };

    function init() {
        createStars();
        initializeTheme();
        initializeRevealAnimations();
        initializePointerEffects();
        initializeTiltCards();
        initializeMagneticElements();
        initializeRipples();
        initializeSkipLink();
        initializeForm();
        initializeResultActions();
        initializeDemo();
        checkHealth();
        syncInterestChips();
        updateAllSummaries();
        updateConstraintCount();

        window.addEventListener("online", checkHealth);
        window.addEventListener("offline", () => {
            setSystemStatus(
                "Offline",
                "offline",
                "You are offline. Existing results remain available, but a new plan needs a connection.",
            );
        });
    }

    function initializeSkipLink() {
        dom.skipLink?.addEventListener("click", (event) => {
            if (!dom.plannerSection) {
                return;
            }

            event.preventDefault();
            dom.plannerSection.scrollIntoView({
                behavior: prefersReducedMotion ? "auto" : "smooth",
                block: "start",
            });
            dom.plannerSection.focus({ preventScroll: true });
        });
    }

    // ---------------------------------------------------------------------
    // Theme
    // ---------------------------------------------------------------------

    function initializeTheme() {
        let savedTheme = null;

        try {
            savedTheme = window.localStorage.getItem("weekendia-theme");
        } catch (_error) {
            savedTheme = null;
        }

        const theme = savedTheme === "light" || savedTheme === "dark"
            ? savedTheme
            : "dark";

        applyTheme(theme);

        dom.themeToggle?.addEventListener("click", () => {
            const nextTheme = dom.body.dataset.theme === "dark" ? "light" : "dark";
            applyTheme(nextTheme, true);
        });
    }

    function applyTheme(theme, persist = false) {
        dom.body.dataset.theme = theme;
        dom.themeToggle?.setAttribute(
            "aria-label",
            theme === "dark" ? "Switch to light theme" : "Switch to dark theme",
        );

        if (dom.themeColor) {
            dom.themeColor.setAttribute("content", theme === "dark" ? "#07101d" : "#edf6fb");
        }

        if (persist) {
            try {
                window.localStorage.setItem("weekendia-theme", theme);
            } catch (_error) {
                // Some browsers restrict localStorage in private browsing mode.
            }
        }
    }

    // ---------------------------------------------------------------------
    // Decorative stars and pointer light
    // ---------------------------------------------------------------------

    function createStars() {
        if (!dom.starField) {
            return;
        }

        const count = window.innerWidth < 480 ? 18 : window.innerWidth < 760 ? 24 : 64;
        const fragment = document.createDocumentFragment();

        for (let index = 0; index < count; index += 1) {
            const star = document.createElement("span");
            const size = (Math.random() * 1.9 + 0.65).toFixed(2);
            star.style.setProperty("--star-x", `${(Math.random() * 100).toFixed(2)}%`);
            star.style.setProperty("--star-y", `${(Math.random() * 100).toFixed(2)}%`);
            star.style.setProperty("--star-size", `${size}px`);
            star.style.setProperty("--star-opacity", (Math.random() * 0.55 + 0.2).toFixed(2));
            star.style.setProperty("--star-duration", `${(Math.random() * 3.8 + 2.2).toFixed(2)}s`);
            star.style.setProperty("--star-delay", `${(Math.random() * -5).toFixed(2)}s`);
            fragment.appendChild(star);
        }

        dom.starField.appendChild(fragment);
    }

    function initializePointerEffects() {
        if (!supportsFinePointer || prefersReducedMotion) {
            return;
        }

        window.addEventListener("pointermove", (event) => {
            if (state.pointerFrame) {
                window.cancelAnimationFrame(state.pointerFrame);
            }

            state.pointerFrame = window.requestAnimationFrame(() => {
                dom.root.style.setProperty("--mouse-x", `${event.clientX}px`);
                dom.root.style.setProperty("--mouse-y", `${event.clientY}px`);
            });
        }, { passive: true });

        if (dom.plannerShell) {
            let plannerBounds = null;
            let plannerFrame = null;
            let plannerPoint = null;

            dom.plannerShell.addEventListener("pointerenter", () => {
                plannerBounds = dom.plannerShell.getBoundingClientRect();
            });

            dom.plannerShell.addEventListener("pointermove", (event) => {
                plannerPoint = { x: event.clientX, y: event.clientY };
                if (plannerFrame) {
                    return;
                }

                plannerFrame = window.requestAnimationFrame(() => {
                    plannerFrame = null;
                    plannerBounds ||= dom.plannerShell.getBoundingClientRect();
                    const x = ((plannerPoint.x - plannerBounds.left) / plannerBounds.width) * 100;
                    const y = ((plannerPoint.y - plannerBounds.top) / plannerBounds.height) * 100;
                    dom.plannerShell.style.setProperty("--planner-x", `${x.toFixed(2)}%`);
                    dom.plannerShell.style.setProperty("--planner-y", `${y.toFixed(2)}%`);
                });
            });

            dom.plannerShell.addEventListener("pointerleave", () => {
                plannerBounds = null;
                if (plannerFrame) {
                    window.cancelAnimationFrame(plannerFrame);
                    plannerFrame = null;
                }
            });

            window.addEventListener("resize", () => {
                plannerBounds = null;
            }, { passive: true });
        }
    }

    // ---------------------------------------------------------------------
    // Reveal, tilt, magnetic and ripple micro-interactions
    // ---------------------------------------------------------------------

    function initializeRevealAnimations() {
        const revealElements = Array.from(document.querySelectorAll("[data-reveal]"));

        revealElements.forEach((element) => {
            const delay = Number(element.dataset.revealDelay || 0);
            element.style.setProperty("--reveal-delay", `${delay}ms`);
        });

        if (prefersReducedMotion || !("IntersectionObserver" in window)) {
            revealElements.forEach((element) => element.classList.add("is-visible"));
            return;
        }

        const observer = new IntersectionObserver((entries, currentObserver) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add("is-visible");
                currentObserver.unobserve(entry.target);
            });
        }, {
            rootMargin: "0px 0px -8% 0px",
            threshold: 0.12,
        });

        revealElements.forEach((element) => observer.observe(element));
    }

    function revealInside(container) {
        if (!container) {
            return;
        }

        const elements = container.matches("[data-reveal]")
            ? [container, ...container.querySelectorAll("[data-reveal]")]
            : Array.from(container.querySelectorAll("[data-reveal]"));

        window.requestAnimationFrame(() => {
            elements.forEach((element, index) => {
                window.setTimeout(() => element.classList.add("is-visible"), index * 70);
            });
        });
    }

    function initializeTiltCards() {
        if (!supportsFinePointer || prefersReducedMotion) {
            return;
        }

        document.querySelectorAll(".tilt-card").forEach((card) => {
            const strength = Number(card.dataset.tiltStrength || 6);
            let bounds = null;
            let frame = null;
            let point = null;

            card.addEventListener("pointerenter", () => {
                bounds = card.getBoundingClientRect();
            });

            card.addEventListener("pointermove", (event) => {
                point = { x: event.clientX, y: event.clientY };
                if (frame) {
                    return;
                }

                frame = window.requestAnimationFrame(() => {
                    frame = null;
                    bounds ||= card.getBoundingClientRect();
                    const normalizedX = (point.x - bounds.left) / bounds.width;
                    const normalizedY = (point.y - bounds.top) / bounds.height;
                    const rotateY = (normalizedX - 0.5) * strength * 2;
                    const rotateX = (0.5 - normalizedY) * strength * 1.45;

                    card.style.animationPlayState = "paused";
                    card.style.transform = `rotateX(${(rotateX + 4).toFixed(2)}deg) rotateY(${(rotateY - 7).toFixed(2)}deg) translateZ(24px)`;
                    card.style.setProperty("--card-x", `${(normalizedX * 100).toFixed(2)}%`);
                    card.style.setProperty("--card-y", `${(normalizedY * 100).toFixed(2)}%`);
                });
            });

            card.addEventListener("pointerleave", () => {
                bounds = null;
                if (frame) {
                    window.cancelAnimationFrame(frame);
                    frame = null;
                }
                card.style.transform = "rotateY(-7deg) rotateX(4deg) translateZ(24px)";
                window.setTimeout(() => {
                    card.style.animationPlayState = "running";
                }, 220);
            });
        });
    }

    function initializeMagneticElements() {
        if (!supportsFinePointer || prefersReducedMotion) {
            return;
        }

        document.querySelectorAll(".magnetic").forEach((element) => {
            let bounds = null;
            let frame = null;
            let point = null;

            element.addEventListener("pointerenter", () => {
                bounds = element.getBoundingClientRect();
            });

            element.addEventListener("pointermove", (event) => {
                point = { x: event.clientX, y: event.clientY };
                if (frame) {
                    return;
                }

                frame = window.requestAnimationFrame(() => {
                    frame = null;
                    bounds ||= element.getBoundingClientRect();
                    const x = point.x - bounds.left - bounds.width / 2;
                    const y = point.y - bounds.top - bounds.height / 2;
                    const factor = element.classList.contains("submit-button") ? 0.08 : 0.12;
                    element.style.transform = `translate(${(x * factor).toFixed(2)}px, ${(y * factor).toFixed(2)}px)`;
                });
            });

            element.addEventListener("pointerleave", () => {
                bounds = null;
                if (frame) {
                    window.cancelAnimationFrame(frame);
                    frame = null;
                }
                element.style.transform = "";
            });
        });
    }

    function initializeRipples() {
        document.querySelectorAll(".ripple-host").forEach((element) => {
            element.addEventListener("pointerdown", (event) => {
                const rect = element.getBoundingClientRect();
                const ripple = document.createElement("span");
                ripple.className = "ripple";
                ripple.style.left = `${event.clientX - rect.left}px`;
                ripple.style.top = `${event.clientY - rect.top}px`;
                element.appendChild(ripple);
                window.setTimeout(() => ripple.remove(), 760);
            });
        });
    }

    // ---------------------------------------------------------------------
    // Form
    // ---------------------------------------------------------------------

    function initializeForm() {
        if (!dom.plannerForm) {
            return;
        }

        dom.choiceChips.forEach((chip) => {
            chip.addEventListener("click", () => toggleInterest(chip));
        });

        Object.entries(fields).forEach(([name, field]) => {
            if (!field) {
                return;
            }

            field.addEventListener("input", () => {
                clearFieldError(name);
                updateAllSummaries();

                if (field.tagName === "TEXTAREA") {
                    autoResizeTextarea(field);
                }

                if (name === "interests") {
                    syncInterestChips();
                }

                if (name === "constraints") {
                    updateConstraintCount();
                }
            });

            field.addEventListener("change", () => {
                clearFieldError(name);
                updateAllSummaries();
            });
        });

        dom.plannerForm.addEventListener("submit", submitPlan);

        document.addEventListener("keydown", (event) => {
            const isShortcut = (event.ctrlKey || event.metaKey) && event.key === "Enter";
            if (!isShortcut || state.isSubmitting) {
                return;
            }

            event.preventDefault();
            dom.plannerForm.requestSubmit();
        });
    }

    function toggleInterest(chip) {
        const value = chip.dataset.interest?.trim();
        if (!value || !dom.interests) {
            return;
        }

        const currentValues = parseInterestValues(dom.interests.value);
        const existingIndex = currentValues.findIndex(
            (item) => item.toLocaleLowerCase("en-US") === value.toLocaleLowerCase("en-US"),
        );

        if (existingIndex >= 0) {
            currentValues.splice(existingIndex, 1);
        } else {
            currentValues.push(value);
        }

        dom.interests.value = currentValues.join(", ");
        dom.interests.dispatchEvent(new Event("input", { bubbles: true }));
    }

    function parseInterestValues(value) {
        return value
            .split(/[,;\n]+/)
            .map((item) => item.trim())
            .filter(Boolean)
            .filter((item, index, array) => array.findIndex(
                (candidate) => candidate.toLocaleLowerCase("en-US") === item.toLocaleLowerCase("en-US"),
            ) === index);
    }

    function syncInterestChips() {
        if (!dom.interests) {
            return;
        }

        const values = parseInterestValues(dom.interests.value)
            .map((item) => item.toLocaleLowerCase("en-US"));

        dom.choiceChips.forEach((chip) => {
            const value = chip.dataset.interest?.toLocaleLowerCase("en-US") || "";
            chip.classList.toggle("is-selected", values.includes(value));
            chip.setAttribute("aria-pressed", String(values.includes(value)));
        });
    }

    function autoResizeTextarea(textarea) {
        textarea.style.height = "auto";
        const minHeight = textarea.id === "constraints" ? 100 : 76;
        textarea.style.height = `${Math.max(textarea.scrollHeight, minHeight)}px`;
    }

    function updateConstraintCount() {
        if (!dom.constraints || !dom.constraintCount) {
            return;
        }

        dom.constraintCount.textContent = String(dom.constraints.value.length);
    }

    function updateAllSummaries() {
        updateSummary(dom.summaryLocation, fields.location?.value, "Not selected yet");
        updateSummary(dom.summaryBudget, fields.budget?.value, "Flexible");

        const groupValue = fields.group_size?.value.trim();
        updateSummary(
            dom.summaryGroup,
            groupValue ? formatGroupSize(groupValue) : "",
            "Not specified",
        );

        updateSummary(dom.summaryWeather, fields.weather?.value, "Waiting for details");
    }

    function updateSummary(element, value, fallback) {
        if (!element) {
            return;
        }

        const normalized = String(value || "").trim();
        element.textContent = normalized || fallback;
        element.closest(".summary-row")?.classList.toggle("has-value", Boolean(normalized));
    }

    function validateForm() {
        clearAllFieldErrors();
        const errors = {};

        const requiredMessages = {
            location: "Enter your city or area.",
            interests: "Enter or select at least one interest.",
            budget: "Enter your total budget.",
            group_size: "Enter the group size.",
            available_time: "Enter your available time.",
            weather: "Enter the expected weather.",
            transport: "Select your transportation.",
        };

        Object.entries(requiredMessages).forEach(([name, message]) => {
            const value = fields[name]?.value?.trim() || "";
            if (!value) {
                errors[name] = message;
            }
        });

        const groupValue = Number(fields.group_size?.value || 0);
        if (fields.group_size?.value && (!Number.isInteger(groupValue) || groupValue < 1 || groupValue > 50)) {
            errors.group_size = "Group size must be a whole number between 1 and 50.";
        }

        Object.entries(errors).forEach(([name, message]) => setFieldError(name, message));

        if (Object.keys(errors).length > 0) {
            const firstField = fields[Object.keys(errors)[0]];
            firstField?.focus({ preventScroll: true });
            firstField?.closest(".field-group")?.scrollIntoView({
                behavior: prefersReducedMotion ? "auto" : "smooth",
                block: "center",
            });
            showToast("Complete the highlighted fields before continuing.", true);
            return false;
        }

        return true;
    }

    function serializeForm() {
        return {
            location: fields.location.value.trim(),
            interests: fields.interests.value.trim(),
            budget: fields.budget.value.trim(),
            group_size: fields.group_size.value.trim(),
            available_time: fields.available_time.value.trim(),
            weather: fields.weather.value.trim(),
            transport: fields.transport.value.trim(),
            constraints: fields.constraints.value.trim(),
        };
    }

    async function submitPlan(event) {
        event.preventDefault();

        if (state.isSubmitting) {
            return;
        }

        if (state.configReady === false) {
            showToast("Planner setup is incomplete. Configure a planner mode before submitting.", true, 6200);
            setSystemStatus("Setup required", "error", "Planner configuration needs attention before a plan can be submitted.");
            return;
        }

        if (!validateForm()) {
            return;
        }

        state.isSubmitting = true;
        setSubmitState(true);
        startLoadingExperience();

        const controller = new AbortController();
        const timeoutId = window.setTimeout(() => controller.abort(), 55_000);

        try {
            const response = await fetch("/api/plan", {
                method: "POST",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(serializeForm()),
                signal: controller.signal,
            });

            const data = await parseJsonResponse(response);

            if (!response.ok || !data.ok) {
                const apiError = new Error(data?.error?.message || "The plan could not be created.");
                apiError.fields = data?.error?.fields || null;
                apiError.code = data?.error?.code || "request_error";
                throw apiError;
            }

            await completeLoadingExperience();
            showResult(data);
            state.configReady = true;
            applyHealthStatus();
        } catch (error) {
            stopLoadingExperience();
            dom.loadingPanel.hidden = true;

            if (error.name === "AbortError") {
                showToast("The request took too long. Check your internet connection or proxy and try again.", true, 6200);
                setSystemStatus(
                    "Planner delayed",
                    "degraded",
                    "The planner request timed out. Your previous result, if any, is still available.",
                );
            } else {
                if (error.fields) {
                    Object.entries(error.fields).forEach(([name, message]) => setFieldError(name, String(message)));
                }

                showToast(error.message || "An unexpected error occurred.", true, 6200);

                if (["configuration_error", "authentication_error"].includes(error.code)) {
                    state.configReady = false;
                    setSystemStatus("Setup required", "error", "Planner configuration needs attention.");
                } else if (!navigator.onLine) {
                    setSystemStatus(
                        "Offline",
                        "offline",
                        "You are offline. Your previous result, if any, is still available.",
                    );
                } else if (error instanceof TypeError) {
                    setSystemStatus(
                        "Status unavailable",
                        "degraded",
                        "The planner could not be reached. Your previous result, if any, is still available.",
                    );
                }
            }

            document.getElementById("planner")?.scrollIntoView({
                behavior: prefersReducedMotion ? "auto" : "smooth",
                block: "start",
            });
        } finally {
            window.clearTimeout(timeoutId);
            state.isSubmitting = false;
            setSubmitState(false);
        }
    }

    async function parseJsonResponse(response) {
        const contentType = response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            const text = await response.text();
            return {
                ok: false,
                error: {
                    message: text.trim() || "The server returned an invalid response.",
                    code: "invalid_server_response",
                },
            };
        }

        return response.json();
    }

    function setSubmitState(isLoading) {
        if (!dom.submitButton) {
            return;
        }

        dom.submitButton.disabled = isLoading;
        dom.submitButton.classList.toggle("is-loading", isLoading);
        dom.submitButton.setAttribute("aria-busy", String(isLoading));

        if (dom.submitLabel) {
            dom.submitLabel.textContent = isLoading
                ? "Building your plan..."
                : "Build my weekend plan";
        }
    }

    function setFieldError(name, message) {
        const field = fields[name];
        const errorElement = document.querySelector(`[data-error-for="${escapeSelector(name)}"]`);

        field?.closest(".input-shell")?.classList.add("is-invalid");
        field?.setAttribute("aria-invalid", "true");

        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add("is-visible");
        }
    }

    function clearFieldError(name) {
        const field = fields[name];
        const errorElement = document.querySelector(`[data-error-for="${escapeSelector(name)}"]`);

        field?.closest(".input-shell")?.classList.remove("is-invalid");
        field?.setAttribute("aria-invalid", "false");

        if (errorElement) {
            errorElement.textContent = "";
            errorElement.classList.remove("is-visible");
        }
    }

    function clearAllFieldErrors() {
        Object.keys(fields).forEach(clearFieldError);
    }

    function escapeSelector(value) {
        if (window.CSS?.escape) {
            return window.CSS.escape(value);
        }
        return String(value).replace(/["\\]/g, "\\$&");
    }

    // ---------------------------------------------------------------------
    // Loading experience
    // ---------------------------------------------------------------------

    function startLoadingExperience() {
        dom.loadingPanel.hidden = false;
        dom.loadingPanel.setAttribute("aria-busy", "true");
        dom.progressRing?.classList.remove("is-complete");

        if (dom.progressValue) {
            dom.progressValue.textContent = "Working";
        }

        if (dom.loadingTitle) {
            dom.loadingTitle.textContent = "Waiting for the planner response...";
        }

        if (dom.loadingDescription) {
            dom.loadingDescription.textContent = "Your request is in progress. Weekendia does not verify live prices, venue availability, or travel conditions.";
        }

        dom.loadingSteps.forEach((step, index) => {
            step.classList.toggle("is-active", index === 0);
            step.classList.remove("is-complete");
        });

        dom.loadingPanel.scrollIntoView({
            behavior: prefersReducedMotion ? "auto" : "smooth",
            block: "center",
        });
    }

    function stopLoadingExperience() {
        dom.loadingPanel?.setAttribute("aria-busy", "false");
    }

    async function completeLoadingExperience() {
        stopLoadingExperience();
        dom.progressRing?.classList.add("is-complete");

        if (dom.progressValue) {
            dom.progressValue.textContent = "Received";
        }

        if (dom.loadingTitle) {
            dom.loadingTitle.textContent = "Planner response received";
        }

        if (dom.loadingDescription) {
            dom.loadingDescription.textContent = "Preparing the response for display.";
        }

        dom.loadingSteps.forEach((step) => {
            step.classList.remove("is-active");
            step.classList.add("is-complete");
        });

        if (!prefersReducedMotion) {
            await wait(180);
        }
    }

    // ---------------------------------------------------------------------
    // Result formatting and actions
    // ---------------------------------------------------------------------

    function initializeResultActions() {
        dom.copyButton?.addEventListener("click", copyCurrentPlan);
        dom.downloadButton?.addEventListener("click", downloadCurrentPlan);
        dom.newPlanButton?.addEventListener("click", resetForNewPlan);
    }

    function showResult(data) {
        state.currentPlan = String(data.plan || "").trim();
        state.currentMeta = data.meta || {};

        if (dom.resultContent) {
            dom.resultContent.innerHTML = formatPlan(state.currentPlan);
        }

        if (dom.resultMeta) {
            dom.resultMeta.innerHTML = buildResultMeta(state.currentMeta);
        }

        if (dom.resultSubtitle) {
            const location = state.currentMeta.location || fields.location?.value || "your selected location";
            dom.resultSubtitle.textContent = `A practical plan tailored to ${location}, your availability, and your budget.`;
        }

        dom.loadingPanel.hidden = true;
        dom.resultSection.hidden = false;
        revealInside(dom.resultSection);

        window.requestAnimationFrame(() => {
            dom.resultSection.scrollIntoView({
                behavior: prefersReducedMotion ? "auto" : "smooth",
                block: "start",
            });
            dom.resultHeading?.focus({ preventScroll: true });

            if (dom.resultAnnouncement) {
                dom.resultAnnouncement.textContent = "Your weekend plan is ready and displayed below.";
            }
        });

        showToast("Your weekend plan is ready.");
    }

    function formatPlan(text) {
        const normalized = String(text || "")
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n")
            .trim();

        if (!normalized) {
            return "<p>No response was received.</p>";
        }

        const lines = normalized.split("\n");
        const output = [];
        let listItems = [];
        let orderedItems = [];

        const flushList = () => {
            if (listItems.length === 0) {
                return;
            }

            output.push(`<ul>${listItems.map((item) => `<li>${formatInline(item)}</li>`).join("")}</ul>`);
            listItems = [];
        };

        const flushOrderedList = () => {
            if (orderedItems.length === 0) {
                return;
            }

            const items = orderedItems.map((item) => {
                const details = item.details.length > 0
                    ? `<ul>${item.details.map((detail) => `<li>${formatInline(detail)}</li>`).join("")}</ul>`
                    : "";
                return `<li value="${escapeHtml(item.number)}"><div class="result-ordered-title"><span class="result-number" aria-hidden="true">${escapeHtml(item.number)}</span><span>${formatInline(item.title)}</span></div>${details}</li>`;
            }).join("");

            output.push(`<ol class="result-ordered-list" role="list">${items}</ol>`);
            orderedItems = [];
        };

        lines.forEach((rawLine) => {
            const line = rawLine.trim();

            if (!line) {
                flushList();
                return;
            }

            if (/^[-_*]{3,}$/.test(line)) {
                flushList();
                flushOrderedList();
                output.push('<div class="result-divider"></div>');
                return;
            }

            const markdownHeading = line.match(/^#{1,4}\s+(.+)$/);
            if (markdownHeading) {
                flushList();
                flushOrderedList();
                const numberedSection = markdownHeading[1].match(/^(\d+)[.)-]?\s+(.+)$/);
                output.push(numberedSection
                    ? buildHeading(numberedSection[2], numberedSection[1])
                    : buildHeading(markdownHeading[1]));
                return;
            }

            const numberedHeading = line.match(/^(\d+)[.)-]\s+(.+)$/);
            if (numberedHeading) {
                flushList();
                orderedItems.push({
                    number: numberedHeading[1],
                    title: numberedHeading[2],
                    details: [],
                });
                return;
            }

            const bullet = line.match(/^[-*•–]\s+(.+)$/);
            if (bullet) {
                if (orderedItems.length > 0) {
                    orderedItems[orderedItems.length - 1].details.push(bullet[1]);
                } else {
                    listItems.push(bullet[1]);
                }
                return;
            }

            const boldOnly = line.match(/^\*\*(.+)\*\*:?$/);
            if (boldOnly) {
                flushList();
                flushOrderedList();
                output.push(`<h4>${formatInline(boldOnly[1])}</h4>`);
                return;
            }

            if (line.endsWith(":") && line.length <= 105) {
                flushList();
                flushOrderedList();
                output.push(`<h4>${formatInline(line.slice(0, -1))}</h4>`);
                return;
            }

            flushList();
            flushOrderedList();
            output.push(`<p>${formatInline(line)}</p>`);
        });

        flushList();
        flushOrderedList();
        return output.join("");
    }

    function buildHeading(title, number = "✦") {
        const cleanedTitle = String(title)
            .replace(/^\*\*(.+)\*\*$/, "$1")
            .trim();

        return `<h3><span class="result-number">${escapeHtml(number)}</span><span>${formatInline(cleanedTitle)}</span></h3>`;
    }

    function formatInline(value) {
        let safe = escapeHtml(value);
        safe = safe.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
        safe = safe.replace(/__(.+?)__/g, "<strong>$1</strong>");
        safe = safe.replace(/`(.+?)`/g, "<strong>$1</strong>");
        return safe;
    }

    function buildResultMeta(meta) {
        const items = [
            { label: "Location", icon: icons.location, text: meta.location || fields.location?.value },
            { label: "Budget", icon: icons.budget, text: meta.budget || fields.budget?.value },
            { label: "Group size", icon: icons.group, text: formatGroupSize(meta.group_size || fields.group_size?.value) },
        ].filter((item) => String(item.text || "").trim());

        return items.map((item) => (
            `<span class="result-meta-chip" aria-label="${escapeHtml(`${item.label}: ${item.text}`)}">${item.icon}<span class="sr-only">${escapeHtml(`${item.label}: `)}</span><span>${escapeHtml(item.text)}</span></span>`
        )).join("");
    }

    async function copyCurrentPlan() {
        if (!state.currentPlan) {
            showToast("There is no plan to copy yet.", true);
            return;
        }

        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(state.currentPlan);
            } else {
                fallbackCopy(state.currentPlan);
            }
            showToast("The plan was copied.");
        } catch (_error) {
            showToast("Your browser did not allow automatic copying.", true);
        }
    }

    function fallbackCopy(text) {
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        textarea.style.pointerEvents = "none";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
    }

    function downloadCurrentPlan() {
        if (!state.currentPlan) {
            showToast("There is no plan to save yet.", true);
            return;
        }

        const header = [
            "Weekendia — Weekend Plan",
            state.currentMeta?.location ? `Location: ${state.currentMeta.location}` : "",
            state.currentMeta?.budget ? `Budget: ${state.currentMeta.budget}` : "",
            "",
        ].filter((line, index) => line || index === 3).join("\n");

        const blob = new Blob(["\uFEFF", header, state.currentPlan], {
            type: "text/plain;charset=utf-8",
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        const date = new Date().toISOString().slice(0, 10);
        link.href = url;
        link.download = `weekendia-plan-${date}.txt`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
        showToast("The plan was saved as a text file.");
    }

    function resetForNewPlan() {
        state.currentPlan = "";
        state.currentMeta = null;
        dom.resultSection.hidden = true;
        if (dom.resultAnnouncement) {
            dom.resultAnnouncement.textContent = "";
        }
        dom.plannerForm?.reset();
        clearAllFieldErrors();
        syncInterestChips();
        updateAllSummaries();
        updateConstraintCount();

        document.querySelectorAll("textarea").forEach((textarea) => {
            textarea.style.height = "";
        });

        document.getElementById("planner")?.scrollIntoView({
            behavior: prefersReducedMotion ? "auto" : "smooth",
            block: "start",
        });

        window.setTimeout(() => fields.location?.focus({ preventScroll: true }), 450);
    }

    // ---------------------------------------------------------------------
    // Demo
    // ---------------------------------------------------------------------

    function initializeDemo() {
        dom.viewDemoButton?.addEventListener("click", openDemo);
        dom.demoClose?.addEventListener("click", closeDemo);

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && dom.demoSection && !dom.demoSection.hidden) {
                event.preventDefault();
                closeDemo();
            }
        });
    }

    function openDemo() {
        if (!dom.demoSection) {
            return;
        }

        state.demoReturnFocus = document.activeElement instanceof HTMLElement
            ? document.activeElement
            : dom.viewDemoButton;
        dom.demoSection.hidden = false;
        dom.viewDemoButton?.setAttribute("aria-expanded", "true");
        revealInside(dom.demoSection);
        dom.demoSection.scrollIntoView({
            behavior: prefersReducedMotion ? "auto" : "smooth",
            block: "center",
        });

        window.requestAnimationFrame(() => {
            dom.demoHeading?.focus({ preventScroll: true });
        });
    }

    function closeDemo() {
        if (!dom.demoSection || dom.demoSection.hidden) {
            return;
        }

        dom.demoSection.hidden = true;
        dom.viewDemoButton?.setAttribute("aria-expanded", "false");
        const returnTarget = state.demoReturnFocus?.isConnected
            ? state.demoReturnFocus
            : dom.viewDemoButton;
        returnTarget?.focus({ preventScroll: true });
        state.demoReturnFocus = null;
    }

    // ---------------------------------------------------------------------
    // Health and status
    // ---------------------------------------------------------------------

    async function checkHealth() {
        if (!navigator.onLine) {
            state.health = null;
            setSystemStatus(
                "Offline",
                "offline",
                "You are offline. Existing results remain available, but a new plan needs a connection.",
            );
            return;
        }

        setSystemStatus("Checking planner", "checking", "Checking the planner configuration.");

        try {
            const response = await fetch("/api/health", {
                headers: { "Accept": "application/json" },
                cache: "no-store",
            });
            const data = await response.json();
            if (!response.ok || data.ok !== true) {
                throw new Error("Health endpoint unavailable");
            }

            state.configReady = Boolean(data.configured);
            state.health = {
                configured: Boolean(data.configured),
                mode: String(data.mode || "invalid"),
                externalProcessing: Boolean(data.external_processing),
            };
            applyHealthStatus();
        } catch (_error) {
            state.configReady = null;
            state.health = null;
            setSystemStatus(
                "Status unavailable",
                "degraded",
                "The planner status could not be checked. Existing results remain available.",
            );
        }
    }

    function applyHealthStatus() {
        if (!state.health) {
            return;
        }

        if (!state.health.configured || state.health.mode === "invalid") {
            setSystemStatus("Setup required", "error", "Planner configuration needs attention.");
            return;
        }

        if (state.health.mode === "demo") {
            setSystemStatus(
                "Demo mode",
                "ready",
                "Local demo mode is configured without external processing.",
            );
            return;
        }

        const processingDetail = state.health.externalProcessing
            ? "Planner configured. Submitted details are processed by an external provider."
            : "Planner configured without external processing.";
        setSystemStatus("Planner configured", "ready", processingDetail);
    }

    function setSystemStatus(text, type, detail = text) {
        if (dom.statusText) {
            dom.statusText.textContent = text;
        }

        dom.systemStatus?.classList.toggle("is-ready", type === "ready");
        dom.systemStatus?.classList.toggle("is-error", type === "error");
        dom.systemStatus?.classList.toggle("is-offline", type === "offline");
        dom.systemStatus?.classList.toggle("is-degraded", type === "degraded");
        dom.systemStatus?.classList.toggle("is-checking", type === "checking");
        dom.systemStatus?.setAttribute("title", detail);
        dom.systemStatus?.setAttribute("aria-label", detail);
        dom.body.classList.toggle("is-offline", type === "offline");
        dom.body.classList.toggle("is-degraded", type === "degraded");
    }

    // ---------------------------------------------------------------------
    // Toast and helpers
    // ---------------------------------------------------------------------

    function showToast(message, isError = false, duration = 3400) {
        if (!dom.toast || !dom.toastMessage) {
            return;
        }

        window.clearTimeout(state.toastTimer);
        dom.toastMessage.textContent = message;
        dom.toast.classList.toggle("is-error", isError);

        if (dom.toastIcon) {
            dom.toastIcon.innerHTML = isError ? icons.error : icons.success;
        }

        dom.toast.classList.add("is-visible");
        state.toastTimer = window.setTimeout(() => {
            dom.toast.classList.remove("is-visible");
        }, duration);
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatGroupSize(value) {
        const text = String(value ?? "").trim();
        if (!text) {
            return "";
        }

        const numericValue = Number(text);
        const unit = numericValue === 1 ? "person" : "people";
        return `${text} ${unit}`;
    }

    function wait(milliseconds) {
        return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
    }

    init();
})();
