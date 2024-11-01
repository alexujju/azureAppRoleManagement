// Fetch assigned roles for the user
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

        const assignedRoles = data.assignedRoles || [];
        const availableRoles = data.availableRoles || [];
        const displayName = data.displayName || email;

        const title = document.createElement('h5');
        title.textContent = `Roles for ${displayName}`;
        resultDiv.appendChild(title);

        const roleList = document.createElement('ul');
        if (assignedRoles.length > 0) {
            assignedRoles.forEach(role => {
                const roleItem = document.createElement('li');
                roleItem.textContent = `${role.displayName} - Assigned on: ${role.assignmentDate || 'N/A'}`;
                
                // Add a checkbox for removal
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = role.id; // Role ID for removal
                checkbox.classList.add('role-checkbox'); // Optional: add a class for easy selection
                
                // Append checkbox to the list item
                roleItem.prepend(checkbox);
                roleList.appendChild(roleItem);
            });
        } else {
            roleList.innerHTML = `<li>No roles assigned.</li>`;
        }
        resultDiv.appendChild(roleList);

        document.getElementById('assignRolesSection').style.display = 'block';
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
        if (!assignedRoles.some(assignedRole => assignedRole.id === role.id)) {
            const option = document.createElement('option');
            option.value = role.id;
            option.textContent = role.displayName;
            roleDropdown.appendChild(option);
        }
    });
}

// Handle role assignment
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('roleAssignmentForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        console.log('Role assignment form submitted.'); // Debug line

        const email = document.getElementById('email').value;
        const selectedRoleIds = Array.from(document.getElementById('roleDropdown').selectedOptions).map(option => option.value);
        console.log('Selected role IDs:', selectedRoleIds); // Debug line
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = 'Assigning roles...';

        if (!selectedRoleIds.length) {
            resultDiv.innerHTML = 'Please select at least one role to assign.';
            return;
        }

        // Send the role assignment request
        fetch('/assign_roles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, role_ids: selectedRoleIds })
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
            // Display success message
            resultDiv.innerHTML = data.message;

            // Optionally, refresh the assigned roles after successful assignment
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
                // Refresh the displayed roles
                const assignedRoles = data.assignedRoles || [];
                resultDiv.innerHTML = `Roles for ${email}:`;
                const roleList = document.createElement('ul');
                assignedRoles.forEach(role => {
                    const roleItem = document.createElement('li');
                    roleItem.textContent = `${role.displayName} - Assigned on: ${role.assignmentDate || 'N/A'}`;

                    // Add a checkbox for removal
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.value = role.id; // Role ID for removal
                    checkbox.classList.add('role-checkbox'); // Optional: add a class for easy selection
                
                    roleItem.prepend(checkbox);
                    roleList.appendChild(roleItem);
                });
                resultDiv.appendChild(roleList);
            })
            .catch(error => {
                console.error('Error fetching updated roles:', error);
                resultDiv.innerHTML = `Error fetching updated roles: ${error.message}.`;
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
            resultDiv.innerHTML = `Error assigning roles: ${error.message}. Please try again.`;
        });
    });
});

// Function to remove selected roles
function removeSelectedRoles() {
    const selectedCheckboxes = document.querySelectorAll('.role-checkbox:checked');
    const roleIdsToRemove = Array.from(selectedCheckboxes).map(checkbox => checkbox.value);

    if (roleIdsToRemove.length === 0) {
        alert('Please select at least one role to remove.');
        return;
    }

    // Send the removal request to the server
    fetch('/remove_roles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role_ids: roleIdsToRemove })
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
        // Refresh the assigned roles display after removal
        alert(data.message); // Show success message
        // Call the function to fetch and display updated assigned roles
        fetch('/user_roles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: document.getElementById('email').value })
        })
        .then(response => response.json())
        .then(data => {
            const assignedRoles = data.assignedRoles || [];
            displayAssignedRoles(assignedRoles); // Call to display updated roles
        });
    })
    .catch(error => {
        console.error('Error removing roles:', error);
        alert(`Error removing roles: ${error.message}. Please try again.`);
    });
}

// Add event listener for the remove roles button
document.getElementById('removeRoleButton').addEventListener('click', removeSelectedRoles);
