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

      // Clear loading message / previous content
      activitiesList.innerHTML = "";

      // Reset activity select (keep placeholder)
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // helper to generate initials
      function getInitials(name) {
        if (!name) return "";
        const parts = String(name).trim().split(/\s+/).filter(Boolean);
        if (parts.length === 0) return "";
        if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
        return (parts[0][0] + parts[1][0]).toUpperCase();
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - (details.participants?.length || 0);

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Create participants list
        const participantsUl = document.createElement("ul");
        if (Array.isArray(details.participants) && details.participants.length > 0) {
          participantsUl.className = "participants no-bullets";
          details.participants.forEach((p) => {
            const display = typeof p === "string" ? p : (p.name || p.email || String(p));
            const li = document.createElement("li");

            const avatar = document.createElement("span");
            avatar.className = "participant-avatar";
            avatar.textContent = getInitials(display);

            const nameSpan = document.createElement("span");
            nameSpan.className = "participant-name";
            nameSpan.textContent = display;

            // Delete icon
            const deleteIcon = document.createElement("span");
            deleteIcon.className = "delete-icon";
            deleteIcon.title = "Remove participant";
            deleteIcon.innerHTML = "&#128465;"; // Unicode trash can
            deleteIcon.style.cursor = "pointer";
            deleteIcon.style.marginLeft = "8px";
            deleteIcon.onclick = async () => {
              if (confirm(`Remove ${display} from ${name}?`)) {
                try {
                  const response = await fetch(`/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(display)}`, {
                    method: "POST"
                  });
                  if (response.ok) {
                    fetchActivities();
                  } else {
                    const result = await response.json();
                    alert(result.detail || "Failed to remove participant.");
                  }
                } catch (err) {
                  alert("Error removing participant.");
                }
              }
            };

            li.appendChild(avatar);
            li.appendChild(nameSpan);
            li.appendChild(deleteIcon);
            participantsUl.appendChild(li);
          });
        } else {
          participantsUl.className = "participants empty";
          const li = document.createElement("li");
          li.textContent = "No participants yet — be the first to sign up!";
          participantsUl.appendChild(li);
        }

        activityCard.appendChild(participantsUl);
        activitiesList.appendChild(activityCard);

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
        fetchActivities(); // Refresh the activities list
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
