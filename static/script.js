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

    // Make a POST request to the backend
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
        if (data.length > 0) {
            const displayName = data[0].DisplayName;
            const applicationDisplayName = data[0].applicationDisplayName;

            // Add title
            const title = document.createElement('h5');
            title.textContent = `Roles for ${displayName} (${applicationDisplayName})`;
            resultDiv.appendChild(title);

            // Create list for roles
            const roleList = document.createElement('ul');
            data.forEach(role => {
                const roleItem = document.createElement('li');
                roleItem.textContent = `${role.roleName} - Assigned on: ${new Date(role.assignmentDate).toLocaleString()}`;
                roleList.appendChild(roleItem);
            });
            resultDiv.appendChild(roleList);
        } else {
            resultDiv.textContent = `No roles found for ${email}.`;
        }
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        resultDiv.innerHTML = `Error fetching roles: ${error.message}. Please try again.`;
    });
});
