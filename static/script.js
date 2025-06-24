document.addEventListener('DOMContentLoaded', function() {
    const loginSection = document.getElementById('loginSection');
    const adminLoginSection = document.getElementById('adminLoginSection');
    const adminSection = document.getElementById('adminSection');
    const userSection = document.getElementById('userSection');
    const logoutBtn = document.getElementById('logoutBtn');

    function showSection(section) {
        loginSection.style.display = 'none';
        adminLoginSection.style.display = 'none';
        adminSection.style.display = 'none';
        userSection.style.display = 'none';
        if (section) section.style.display = '';
    }

    function setLogoutVisible(visible) {
        logoutBtn.style.display = visible ? '' : 'none';
    }

    // --- User Login ---
    document.getElementById('loginBtn').onclick = function() {
        fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showSection(userSection);
                setLogoutVisible(true);
                loadHistory();
                document.getElementById('loginMsg').textContent = '';
            } else {
                document.getElementById('loginMsg').textContent = data.message;
            }
        });
    };

    // --- Admin Controls Button ---
    document.getElementById('adminControlsBtn').onclick = function() {
        showSection(adminLoginSection);
    };

    // --- Admin Login ---
    document.getElementById('adminLoginBtn').onclick = function() {
        fetch('/admin_login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                username: document.getElementById('adminUsername').value,
                password: document.getElementById('adminPassword').value
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showSection(adminSection);
                setLogoutVisible(true);
                document.getElementById('adminLoginMsg').textContent = '';
            } else {
                document.getElementById('adminLoginMsg').textContent = data.message;
            }
        });
    };

    // --- Cancel Admin Login ---
    document.getElementById('cancelAdminLoginBtn').onclick = function() {
        showSection(loginSection);
        document.getElementById('adminLoginMsg').textContent = '';
    };

    // --- Logout ---
    logoutBtn.onclick = function() {
        fetch('/logout', {method: 'POST'})
        .then(() => {
            showSection(loginSection);
            setLogoutVisible(false);
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            document.getElementById('adminUsername').value = '';
            document.getElementById('adminPassword').value = '';
        });
    };

    // --- Admin: Create User ---
    document.getElementById('createUserBtn').onclick = function() {
        fetch('/admin/create_user', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: document.getElementById('newUser').value})
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('adminMsg').textContent = data.message +
                (data.generated_password ? ` | Password: ${data.generated_password}` : '');
        });
    };

    // --- Admin: Reset Password ---
    document.getElementById('resetPasswordBtn').onclick = function() {
        fetch('/admin/reset_password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: document.getElementById('resetUser').value})
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('adminMsg').textContent = data.message +
                (data.new_password ? ` | New Password: ${data.new_password}` : '');
        });
    };

    // --- User: Search Drug ---
    document.getElementById('searchBtn').onclick = function() {
        fetch('/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({drug_name: document.getElementById('drugName').value})
        })
        .then(res => res.json())
        .then(data => {
            let infoDiv = document.getElementById('drugInfo');
            if (data.success && data.drug_info) {
                let d = data.drug_info;
                infoDiv.innerHTML = `
                    <strong>Name:</strong> ${d.name}<br>
                    <strong>Generic Name:</strong> ${d.generic_name}<br>
                    <strong>Uses:</strong> ${d.uses}<br>
                    <strong>Side Effects:</strong> ${d.side_effects}<br>
                    <strong>Dosage:</strong> ${d.dosage}<br>
                    <strong>Ingredients:</strong> ${d.ingredients}<br>
                    <strong>Warnings:</strong> ${d.warnings}<br>
                    <strong>Mechanism:</strong> ${d.mechanism}<br>
                    <strong>Last Updated:</strong> ${d.last_updated}
                `;
            } else {
                infoDiv.textContent = data.message || "No information found.";
            }
            loadHistory();
        });
    };

    // --- Load User Search History ---
    function loadHistory() {
        fetch('/user/history')
        .then(res => res.json())
        .then(data => {
            let list = document.getElementById('historyList');
            list.innerHTML = '';
            if (data.success && data.history) {
                data.history.slice(-10).reverse().forEach(item => {
                    let li = document.createElement('li');
                    li.textContent = `${item.drug_name} (${item.timestamp.split('T')[0]})`;
                    list.appendChild(li);
                });
            }
        });
    }

    // On load, show login section and hide logout
    showSection(loginSection);
    setLogoutVisible(false);
});
