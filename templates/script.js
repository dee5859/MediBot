// Simulated login functionality
$(document).ready(function() {
    // View management
    function showView(viewId) {
        $('#loginView, #mainMenu, #searchView, #adminView').addClass('d-none');
        $(`#${viewId}`).removeClass('d-none');
    }
    
    // Login functionality
    $('#loginBtn, #adminLoginBtn').click(function() {
        const username = $('#usernameInput').val() || 'demo_user';
        const isAdmin = $(this).attr('id') === 'adminLoginBtn';
        
        $('#username').text(username);
        showView('mainMenu');
        
        if (isAdmin) {
            $('#adminBtn').click();
        }
    });
    
    // Navigation
    $('#searchBtn').click(() => showView('searchView'));
    $('#adminBtn').click(() => showView('adminView'));
    $('#backToMainFromSearch, #backToMainFromAdmin').click(() => showView('mainMenu'));
    $('#logoutBtn').click(() => showView('loginView'));
    
    // Medicine search
    $('#searchDrugBtn').click(function() {
        const drugName = $('#drugSearchInput').val() || 'Aspirin';
        searchMedicine(drugName);
    });
    
    // Generate password
    $('#generatePasswordBtn').click(function() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
        let password = '';
        for (let i = 0; i < 12; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        $('#tempPassword').val(password);
    });
});

// Simulated medicine search
function searchMedicine(drugName) {
    const results = `
        <div class="medibot-card p-4 mb-4 fade-in">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h3 class="mb-0">${drugName} Information</h3>
                <span class="badge bg-success">Found</span>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="info-section mb-3">
                        <h5><i class="fas fa-tag me-2"></i>Brand Name</h5>
                        <p>${drugName}</p>
                    </div>
                    <div class="info-section mb-3">
                        <h5><i class="fas fa-dna me-2"></i>Generic Name</h5>
                        <p>Acetylsalicylic acid</p>
                    </div>
                    <div class="info-section mb-3">
                        <h5><i class="fas fa-capsules me-2"></i>Primary Uses</h5>
                        <p>Pain relief, fever reduction, anti-inflammatory</p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="info-section mb-3">
                        <h5><i class="fas fa-exclamation-triangle me-2"></i>Side Effects</h5>
                        <ul>
                            <li>Upset stomach</li>
                            <li>Heartburn</li>
                            <li>Drowsiness</li>
                            <li>Mild headache</li>
                        </ul>
                    </div>
                    <div class="info-section">
                        <h5><i class="fas fa-hand-holding-medical me-2"></i>Dosage Information</h5>
                        <p>325-650 mg every 4 hours as needed, not to exceed 4g in 24 hours</p>
                    </div>
                </div>
            </div>
            <div class="mt-4">
                <p class="text-muted"><i class="fas fa-sync-alt me-1"></i>Last updated: ${new Date().toLocaleString()}</p>
            </div>
        </div>
    `;
    $('#searchResults').html(results);
}
