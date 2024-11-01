document.getElementById('userRoleForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    const email = document.getElementById('email').value;
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = 'Fetching roles...';

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        resultDiv.innerHTML = 'Please enter a valid email address.';
        return;
    }

    // Fetch assigned roles for the user
    fetch('/user_roles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errData => {
                throw new Error(errData.error || 'Network response was not ok');
            });
        }
        return response.json(); // Parse the JSON from the response
    })
    .then(data => {
        // Clear previous results
        resultDiv.innerHTML = '';

        // Check if data has roles
        const assignedRoles = data.assignedRoles || [];
        const availableRoles = data.availableRoles || [];
        const displayName = data.displayName || email;

        // Display assigned roles
        const title = document.createElement('h5');
        title.textContent = `Roles for ${displayName}`;
        resultDiv.appendChild(title);

        const roleList = document.createElement('ul');
        if (assignedRoles.length > 0) {
            assignedRoles.forEach(role => {
                const roleItem = document.createElement('li');
                roleItem.textContent = `${role.displayName} - Assigned on: N/A`; // Update with actual assignment date if available
                roleList.appendChild(roleItem);
            });
        } else {
            roleList.innerHTML = `<li>No roles assigned.</li>`;
        }
        resultDiv.appendChild(roleList);

        // Show the assign roles section
        document.getElementById('assignRolesSection').style.display = 'block';

        // Populate the dropdown with available roles excluding assigned ones
        fetchRoles(assignedRoles, availableRoles);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        resultDiv.innerHTML = `Error fetching roles: ${error.message}. Please try again.`;
    });
});

// Fetch available roles for dropdown, filtering out assigned roles
function fetchRoles(assignedRoles, availableRoles) {
    const roleDropdown = document.getElementById('roleDropdown');
    roleDropdown.innerHTML = '';  // Clear previous options
    
    availableRoles.forEach(role => {
        // Only add roles that are not in the assignedRoles array
        if (!assignedRoles.some(assignedRole => assignedRole.id === role.id)) {
            const option = document.createElement('option');
            option.value = role.id;
            option.textContent = role.displayName;
            roleDropdown.appendChild(option);
        }
    });
}
