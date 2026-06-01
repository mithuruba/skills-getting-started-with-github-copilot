document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      // Reset activity select to avoid duplicate options when refreshing
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsContent = details.participants.length
          ? `<ul class="participants-list">${details.participants
              .map((email) => `<li><span class="participant-email">${email}</span><button class="remove-participant" data-activity="${encodeURIComponent(
                name
              )}" data-email="${email}" aria-label="Remove participant" title="Remove participant">✕</button></li>`)
              .join("")}</ul>`
          : `<p class="participants-none">No participants yet</p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <p><strong>Participants:</strong></p>
            ${participantsContent}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Attach remove handlers for each participant button
        activityCard.querySelectorAll('.remove-participant').forEach((btn) => {
          btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const email = btn.dataset.email;
            const activityName = decodeURIComponent(btn.dataset.activity);
            try {
              const res = await fetch(
                `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(email)}`,
                { method: 'DELETE' }
              );
              const result = await res.json();
              if (res.ok) {
                messageDiv.textContent = result.message;
                messageDiv.className = 'success';
                // Refresh the activities list to reflect removal
                fetchActivities();
              } else {
                messageDiv.textContent = result.detail || 'Failed to remove participant';
                messageDiv.className = 'error';
              }
              messageDiv.classList.remove('hidden');
              setTimeout(() => {
                messageDiv.classList.add('hidden');
              }, 3000);
            } catch (err) {
              messageDiv.textContent = 'Failed to remove participant. Please try again.';
              messageDiv.className = 'error';
              messageDiv.classList.remove('hidden');
              console.error('Error removing participant:', err);
            }
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh the activities list so new participant appears immediately
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
