// RK Health Main Application Controller

// Global App State
let currentUser = null;
let currentTheme = localStorage.getItem('theme') || 'dark';

// Model Datasets
let appointments = [];
let medications = [];
let healthNotes = [];

// Pagination State
let apptCurrentPage = 1;
const apptPageSize = 5;

// Chart instance
let medsChart = null;

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Session verification
    currentUser = await Auth.checkSession();
    if (!currentUser) {
        window.location.href = '/login';
        return;
    }
    
    // Set UI user info
    document.getElementById('display-username').textContent = currentUser.username;
    document.getElementById('user-avatar').textContent = currentUser.username.charAt(0).toUpperCase();
    
    // 2. Initialize Theme
    applyTheme(currentTheme);
    document.getElementById('theme-toggle-btn').addEventListener('click', toggleTheme);
    
    // 3. Setup Navigation
    setupNavigation();
    
    // 4. Setup Event Listeners
    setupFormListeners();
    setupTableActions();
    setupSearchFilters();
    setupDashboardActions();
    
    // 5. Load default view (Dashboard stats & charts)
    loadDashboardData();
});

/* --- THEME CONTROLLER --- */
function applyTheme(theme) {
    const icon = document.getElementById('theme-toggle-btn').querySelector('i');
    if (theme === 'light') {
        document.body.classList.add('light-theme');
        icon.className = 'fa-solid fa-sun';
    } else {
        document.body.classList.remove('light-theme');
        icon.className = 'fa-solid fa-moon';
    }
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(currentTheme);
    // Redraw charts to match grid colors if initialized
    if (medsChart) {
        initMedsChart();
    }
}

/* --- NAVIGATION & SIDEBAR --- */
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Toggle active classes
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            // Switch views
            const targetViewId = item.getAttribute('data-target');
            document.querySelectorAll('.page-view').forEach(view => {
                view.classList.remove('active');
            });
            document.getElementById(targetViewId).classList.add('active');
            
            // Update Title
            const titleText = item.textContent.trim();
            document.getElementById('page-title').textContent = titleText;
            
            // Handle Action Button toggle in Navbar
            const quickAction = document.getElementById('quick-action-btn');
            if (targetViewId === 'medications-view') {
                quickAction.innerHTML = '<i class="fa-solid fa-plus"></i> New Medication';
                quickAction.onclick = () => openMedModal();
                quickAction.style.display = 'inline-flex';
            } else if (targetViewId === 'notes-view') {
                quickAction.innerHTML = '<i class="fa-solid fa-plus"></i> New Note';
                quickAction.onclick = () => openNoteModal();
                quickAction.style.display = 'inline-flex';
            } else if (targetViewId === 'ai-summary-view') {
                quickAction.style.display = 'none';
            } else {
                quickAction.innerHTML = '<i class="fa-solid fa-plus"></i> New Appointment';
                quickAction.onclick = () => openApptModal();
                quickAction.style.display = 'inline-flex';
            }
            
            // Mobile auto collapse
            sidebar.classList.remove('active');
            
            // Load pages data
            if (targetViewId === 'appointments-view') loadAppointments();
            if (targetViewId === 'medications-view') loadMedications();
            if (targetViewId === 'notes-view') loadNotes();
            if (targetViewId === 'ai-summary-view') loadAISummary();
            if (targetViewId === 'dashboard-view') loadDashboardData();
        });
    });
    
    // Mobile responsive toggle
    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
    
    // Logout btn
    document.getElementById('logout-btn').addEventListener('click', () => {
        Auth.logout();
    });
}

/* --- DATA FETCHING & UI GENERATORS --- */

// A. DASHBOARD VIEW DATA
async function loadDashboardData() {
    try {
        // Fetch dashboard statistics
        const response = await fetch('/api/summary/stats');
        if (!response.ok) throw new Error("Failed to load dashboard metrics");
        const stats = await response.json();
        
        // Update stats card badges
        document.getElementById('stat-appointments').textContent = stats.appointments.total;
        document.getElementById('stat-meds-active').textContent = stats.medications.active;
        document.getElementById('stat-notes').textContent = stats.notes.total;
        
        // Fetch recent appointments for summary table
        const apptResponse = await fetch('/api/appointments');
        if (apptResponse.ok) {
            const list = await apptResponse.json();
            const upcoming = list.filter(a => new Date(a.appointment_date) >= new Date().setHours(0,0,0,0)).slice(0, 3);
            renderDashboardAppts(upcoming);
        }
        
        // Fetch medications list to render timeline timeline feed & draw charts
        const medsResponse = await fetch('/api/medications');
        if (medsResponse.ok) {
            medications = await medsResponse.json();
            renderTimelineFeed(medications.filter(m => m.status === 'Active'));
            initMedsChart(stats.medications);
        }
        
    } catch (err) {
        console.error(err);
        Auth.showToast("Could not load dashboard statistics", "danger");
    }
}

function renderDashboardAppts(appts) {
    const tbody = document.getElementById('dashboard-appts-tbody');
    if (appts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-secondary);">No upcoming appointments.</td></tr>`;
        return;
    }
    
    tbody.innerHTML = appts.map(a => `
        <tr>
            <td><strong>${a.patient_name}</strong></td>
            <td>${a.doctor_name}</td>
            <td><i class="fa-regular fa-calendar"></i> ${formatDate(a.appointment_date)}</td>
            <td><i class="fa-regular fa-clock"></i> ${a.appointment_time}</td>
            <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${a.notes || 'None'}</td>
        </tr>
    `).join('');
}

function renderTimelineFeed(meds) {
    const feed = document.getElementById('med-timeline-feed');
    if (meds.length === 0) {
        feed.innerHTML = `
            <div style="text-align: center; color: var(--text-secondary); margin-top: 40px; font-size: 0.9rem;">
                <i class="fa-solid fa-bell-slash" style="font-size: 2rem; margin-bottom: 8px; display: block;"></i>
                No active medication reminders today.
            </div>`;
        return;
    }
    
    feed.innerHTML = meds.map(m => `
        <div class="timeline-item">
            <div class="timeline-time">${m.reminder_time}</div>
            <div class="timeline-details">
                <h4>${m.medicine_name}</h4>
                <p>Dosage: ${m.dosage} | Frequency: ${m.frequency}</p>
            </div>
        </div>
    `).join('');
}

function initMedsChart(medStats) {
    const ctx = document.getElementById('meds-chart').getContext('2d');
    
    if (medsChart) {
        medsChart.destroy();
    }
    
    const isLight = document.body.classList.contains('light-theme');
    const textHex = isLight ? '#0f172a' : '#f8fafc';
    const gridHex = isLight ? '#e5e7eb' : 'rgba(255,255,255,0.06)';
    
    const frequencies = medStats.frequencies || {};
    const labels = Object.keys(frequencies);
    const dataValues = Object.values(frequencies);
    
    medsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.length ? labels : ['Active', 'Completed', 'Paused'],
            datasets: [{
                label: 'Medications Count',
                data: labels.length ? dataValues : [medStats.active, medStats.completed, medStats.paused],
                backgroundColor: [
                    'rgba(79, 70, 229, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(245, 158, 11, 0.7)'
                ],
                borderColor: [
                    '#4f46e5',
                    '#10b981',
                    '#f59e0b'
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    padding: 12,
                    backgroundColor: isLight ? '#ffffff' : '#1e293b',
                    titleColor: textHex,
                    bodyColor: textHex,
                    borderColor: '#4f46e5',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    ticks: { color: textHex },
                    grid: { display: false }
                },
                y: {
                    ticks: { color: textHex, stepSize: 1 },
                    grid: { color: gridHex }
                }
            }
        }
    });
}

// B. APPOINTMENTS VIEW TABLE
async function loadAppointments() {
    const spinner = document.getElementById('appt-spinner');
    spinner.classList.add('active');
    
    const query = document.getElementById('appt-search').value;
    const start = document.getElementById('appt-filter-start').value;
    const end = document.getElementById('appt-filter-end').value;
    
    let url = `/api/appointments?q=${encodeURIComponent(query)}`;
    if (start) url += `&start_date=${start}`;
    if (end) url += `&end_date=${end}`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Appointments loading error");
        appointments = await response.json();
        
        renderAppointmentsTable();
    } catch (err) {
        console.error(err);
        Auth.showToast("Could not retrieve appointments records", "danger");
    } finally {
        spinner.classList.remove('active');
    }
}

function renderAppointmentsTable() {
    const tbody = document.getElementById('appts-table-tbody');
    const startIdx = (apptCurrentPage - 1) * apptPageSize;
    const paginatedAppts = appointments.slice(startIdx, startIdx + apptPageSize);
    
    if (appointments.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-secondary);">No appointments found.</td></tr>`;
        updateApptPagination(0);
        return;
    }
    
    tbody.innerHTML = paginatedAppts.map(a => `
        <tr>
            <td><strong>${a.patient_name}</strong></td>
            <td>${a.doctor_name}</td>
            <td>${formatDate(a.appointment_date)}</td>
            <td>${a.appointment_time}</td>
            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${a.notes}">${a.notes || '<span style="color:var(--text-secondary);">None</span>'}</td>
            <td>
                ${a.google_event_id ? `
                    <span class="badge badge-success" title="${a.google_event_id}"><i class="fa-solid fa-cloud-arrow-up"></i> Synced</span>
                ` : `
                    <span class="badge badge-warning" title="Google synchronization deactivated"><i class="fa-solid fa-cloud-slash"></i> Offline</span>
                `}
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn-icon edit-appt" data-id="${a.id}" title="Edit Appointment"><i class="fa-solid fa-pencil"></i></button>
                    <button class="btn-icon btn-icon-danger delete-appt" data-id="${a.id}" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            </td>
        </tr>
    `).join('');
    
    updateApptPagination(appointments.length);
}

function updateApptPagination(total) {
    const prevBtn = document.getElementById('appt-prev-btn');
    const nextBtn = document.getElementById('appt-next-btn');
    const info = document.getElementById('appt-pagination-info');
    
    const maxPage = Math.ceil(total / apptPageSize);
    prevBtn.disabled = apptCurrentPage <= 1;
    nextBtn.disabled = apptCurrentPage >= maxPage;
    
    const start = total === 0 ? 0 : (apptCurrentPage - 1) * apptPageSize + 1;
    const end = Math.min(apptCurrentPage * apptPageSize, total);
    
    info.textContent = `Showing ${start}-${end} of ${total} entries`;
}

// C. MEDICATIONS VIEW TABLE
async function loadMedications() {
    const spinner = document.getElementById('med-spinner');
    spinner.classList.add('active');
    
    const statusFilter = document.getElementById('med-status-filter').value;
    let url = `/api/medications?status=${statusFilter}`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Medication fetch failure");
        medications = await response.json();
        
        renderMedicationsTable();
    } catch (err) {
        console.error(err);
        Auth.showToast("Failed to fetch medication regimens", "danger");
    } finally {
        spinner.classList.remove('active');
    }
}

function renderMedicationsTable() {
    const tbody = document.getElementById('meds-table-tbody');
    if (medications.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-secondary);">No medication regimens registered.</td></tr>`;
        return;
    }
    
    tbody.innerHTML = medications.map(m => {
        let badgeClass = 'badge-success';
        if (m.status === 'Completed') badgeClass = 'badge-success';
        if (m.status === 'Paused') badgeClass = 'badge-warning';
        
        return `
            <tr>
                <td><strong>${m.medicine_name}</strong></td>
                <td>${m.dosage}</td>
                <td>${m.frequency}</td>
                <td>${m.reminder_time}</td>
                <td><span class="badge ${badgeClass}">${m.status}</span></td>
                <td>
                    ${m.phone_reminder === 1 ? `
                        <span class="badge badge-success"><i class="fa-solid fa-comment-sms"></i> Active</span>
                    ` : `
                        <span class="badge badge-warning"><i class="fa-solid fa-bell-slash"></i> Inactive</span>
                    `}
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon send-sms-test" data-id="${m.id}" title="Send SMS reminder test"><i class="fa-solid fa-paper-plane" style="color:var(--success);"></i></button>
                        <button class="btn-icon edit-med" data-id="${m.id}" title="Edit"><i class="fa-solid fa-pencil"></i></button>
                        <button class="btn-icon btn-icon-danger delete-med" data-id="${m.id}" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// D. HEALTH NOTES CARDS
async function loadNotes() {
    const grid = document.getElementById('notes-grid-container');
    grid.innerHTML = '<div style="text-align:center;grid-column:1/-1;"><div class="spinner" style="margin: 30px auto;"></div></div>';
    
    const query = document.getElementById('notes-search').value;
    const url = `/api/notes?q=${encodeURIComponent(query)}`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Health notes fetching error");
        healthNotes = await response.json();
        
        renderNotesGrid();
    } catch (err) {
        console.error(err);
        Auth.showToast("Could not load health notes logs", "danger");
    }
}

function renderNotesGrid() {
    const grid = document.getElementById('notes-grid-container');
    if (healthNotes.length === 0) {
        grid.innerHTML = `
            <div style="text-align: center; grid-column: 1/-1; color: var(--text-secondary); padding: 40px 0;">
                <i class="fa-solid fa-folder-open" style="font-size: 2.5rem; margin-bottom: 8px;"></i>
                <p>No health logs found. Make a note to record vitals, symptoms or instructions.</p>
            </div>`;
        return;
    }
    
    grid.innerHTML = healthNotes.map(n => `
        <div class="note-card">
            <h4 class="note-card-title">${n.title}</h4>
            <div class="note-card-content">${n.content}</div>
            <div class="note-card-date">
                <span><i class="fa-regular fa-clock"></i> ${formatDate(n.created_at)}</span>
                <div style="display:flex; gap: 4px;">
                    <button class="btn-icon edit-note" data-id="${n.id}" style="width:24px;height:24px;font-size:0.75rem;"><i class="fa-solid fa-pencil"></i></button>
                    <button class="btn-icon btn-icon-danger delete-note" data-id="${n.id}" style="width:24px;height:24px;font-size:0.75rem;"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            </div>
        </div>
    `).join('');
}

// E. AI HEALTH SUMMARY REPORT & MARKDOWN COMPILER
async function loadAISummary(forceGenerate = false) {
    const spinner = document.getElementById('ai-spinner');
    const container = document.getElementById('ai-content-body');
    
    if (forceGenerate) {
        spinner.classList.add('active');
        try {
            const response = await fetch('/api/summary');
            if (!response.ok) throw new Error("AI Summary endpoint failed");
            const data = await response.json();
            
            container.innerHTML = compileMarkdownToHtml(data.summary_markdown);
            Auth.showToast("New AI Health report generated successfully!", "success");
        } catch (err) {
            console.error(err);
            Auth.showToast("Could not generate AI diagnostic report", "danger");
        } finally {
            spinner.classList.remove('active');
        }
    }
}

// Custom Markdown parser for premium rendering
function compileMarkdownToHtml(markdown) {
    if (!markdown) return "<p>No report details found.</p>";
    
    let html = markdown;
    
    // Replace headings (###, ##, #)
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Replace bold (**text**)
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    
    // Replace bullets (- or * list items)
    html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
    // Group adjacent <li> tags inside <ul> tags
    html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
    // Clean up recursive <ul> wrappers
    html = html.replace(/<\/ul>\s*<ul>/gim, '');
    
    // Replace paragraph blocks (any non-empty lines that don't start with headers/lists)
    html = html.split('\n\n').map(p => {
        p = p.trim();
        if (!p) return '';
        if (p.startsWith('<h') || p.startsWith('<ul') || p.startsWith('<li')) return p;
        return `<p>${p}</p>`;
    }).join('\n');
    
    return html;
}

/* --- FORMS & MODAL SUBMISSIONS --- */

function setupFormListeners() {
    // 1. Appointment Form
    document.getElementById('appt-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('appt-id-field').value;
        const payload = {
            patient_name: document.getElementById('appt-patient').value,
            doctor_name: document.getElementById('appt-doctor').value,
            appointment_date: document.getElementById('appt-date').value,
            appointment_time: document.getElementById('appt-time').value,
            notes: document.getElementById('appt-notes').value,
            send_sms: document.getElementById('appt-sms-checkbox').checked
        };
        
        let url = '/api/appointments';
        let method = 'POST';
        
        if (id) {
            url += `/${id}`;
            method = 'PUT';
        }
        
        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                Auth.showToast(id ? "Appointment modified!" : "Appointment scheduled!", "success");
                closeModal('appt-modal');
                loadAppointments();
            } else {
                const data = await res.json();
                Auth.showToast(data.message || "Failed to schedule appointment", "danger");
            }
        } catch (err) {
            console.error(err);
            Auth.showToast("Network error submitting appointment form", "danger");
        }
    });
    
    // 2. Medication Form
    document.getElementById('med-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('med-id-field').value;
        const payload = {
            medicine_name: document.getElementById('med-name').value,
            dosage: document.getElementById('med-dosage').value,
            frequency: document.getElementById('med-frequency').value,
            reminder_time: document.getElementById('med-time').value,
            status: document.getElementById('med-status').value,
            phone_reminder: document.getElementById('med-sms-checkbox').checked
        };
        
        let url = '/api/medications';
        let method = 'POST';
        
        if (id) {
            url += `/${id}`;
            method = 'PUT';
        }
        
        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                Auth.showToast(id ? "Regimen updated!" : "Medication regimen added!", "success");
                closeModal('med-modal');
                loadMedications();
            } else {
                const data = await res.json();
                Auth.showToast(data.message || "Failed to write medication regimen", "danger");
            }
        } catch (err) {
            console.error(err);
            Auth.showToast("Network error submitting medication form", "danger");
        }
    });
    
    // 3. Health Note Form
    document.getElementById('note-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('note-id-field').value;
        const payload = {
            title: document.getElementById('note-title').value,
            content: document.getElementById('note-content').value
        };
        
        let url = '/api/notes';
        let method = 'POST';
        
        if (id) {
            url += `/${id}`;
            method = 'PUT';
        }
        
        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                Auth.showToast(id ? "Health log edited!" : "Health log created!", "success");
                closeModal('note-modal');
                loadNotes();
            } else {
                const data = await res.json();
                Auth.showToast(data.message || "Failed to submit note log", "danger");
            }
        } catch (err) {
            console.error(err);
            Auth.showToast("Network error during note log insertion", "danger");
        }
    });
}

/* --- CRUD TABLE ACTIONS & MODAL OPENERS --- */
function setupTableActions() {
    // A. APPOINTMENTS ACTION HOOKS
    const apptTbody = document.getElementById('appts-table-tbody');
    
    apptTbody.addEventListener('click', async (e) => {
        const editBtn = e.target.closest('.edit-appt');
        const deleteBtn = e.target.closest('.delete-appt');
        
        if (editBtn) {
            const id = editBtn.getAttribute('data-id');
            const appt = appointments.find(a => a.id == id);
            if (appt) openApptModal(appt);
        }
        
        if (deleteBtn) {
            const id = deleteBtn.getAttribute('data-id');
            if (confirm("Are you sure you want to cancel this appointment schedule?")) {
                try {
                    const res = await fetch(`/api/appointments/${id}`, { method: 'DELETE' });
                    if (res.ok) {
                        Auth.showToast("Appointment calendar schedule cancelled.", "success");
                        loadAppointments();
                    } else {
                        Auth.showToast("Cancel request failed", "danger");
                    }
                } catch (err) {
                    console.error(err);
                    Auth.showToast("Network error deleting appointment", "danger");
                }
            }
        }
    });
    
    // B. MEDICATIONS ACTION HOOKS
    const medTbody = document.getElementById('meds-table-tbody');
    
    medTbody.addEventListener('click', async (e) => {
        const editBtn = e.target.closest('.edit-med');
        const deleteBtn = e.target.closest('.delete-med');
        const smsBtn = e.target.closest('.send-sms-test');
        
        if (editBtn) {
            const id = editBtn.getAttribute('data-id');
            const med = medications.find(m => m.id == id);
            if (med) openMedModal(med);
        }
        
        if (smsBtn) {
            const id = smsBtn.getAttribute('data-id');
            Auth.showToast("Triggering Twilio SMS Test Reminder...", "warning");
            try {
                const res = await fetch(`/api/medications/${id}/remind`, { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    if (data.status === 'mocked') {
                        Auth.showToast("SMS simulated successfully (check backend log).", "success");
                    } else {
                        Auth.showToast("SMS sent successfully via Twilio!", "success");
                    }
                } else {
                    Auth.showToast(data.message || "Twilio request failed", "danger");
                }
            } catch (err) {
                console.error(err);
                Auth.showToast("Network error triggering SMS", "danger");
            }
        }
        
        if (deleteBtn) {
            const id = deleteBtn.getAttribute('data-id');
            if (confirm("Are you sure you want to stop this medication scheduler?")) {
                try {
                    const res = await fetch(`/api/medications/${id}`, { method: 'DELETE' });
                    if (res.ok) {
                        Auth.showToast("Medication scheduler stopped.", "success");
                        loadMedications();
                    } else {
                        Auth.showToast("Delete request failed", "danger");
                    }
                } catch (err) {
                    console.error(err);
                    Auth.showToast("Network error deleting medication", "danger");
                }
            }
        }
    });
    
    // C. HEALTH NOTES ACTION HOOKS
    const notesGrid = document.getElementById('notes-grid-container');
    
    notesGrid.addEventListener('click', async (e) => {
        const editBtn = e.target.closest('.edit-note');
        const deleteBtn = e.target.closest('.delete-note');
        
        if (editBtn) {
            const id = editBtn.getAttribute('data-id');
            const note = healthNotes.find(n => n.id == id);
            if (note) openNoteModal(note);
        }
        
        if (deleteBtn) {
            const id = deleteBtn.getAttribute('data-id');
            if (confirm("Permanently delete this health log entry?")) {
                try {
                    const res = await fetch(`/api/notes/${id}`, { method: 'DELETE' });
                    if (res.ok) {
                        Auth.showToast("Health log deleted.", "success");
                        loadNotes();
                    } else {
                        Auth.showToast("Delete request failed", "danger");
                    }
                } catch (err) {
                    console.error(err);
                    Auth.showToast("Network error deleting health note", "danger");
                }
            }
        }
    });
}

// Modal Toggle Helpers
function openApptModal(appt = null) {
    document.getElementById('appt-form').reset();
    const title = document.getElementById('appt-modal-title');
    const idField = document.getElementById('appt-id-field');
    const smsGroup = document.getElementById('appt-sms-group');
    
    if (appt) {
        title.textContent = "Edit Scheduled Appointment";
        idField.value = appt.id;
        document.getElementById('appt-patient').value = appt.patient_name;
        document.getElementById('appt-doctor').value = appt.doctor_name;
        document.getElementById('appt-date').value = appt.appointment_date;
        document.getElementById('appt-time').value = appt.appointment_time;
        document.getElementById('appt-notes').value = appt.notes || '';
        smsGroup.style.display = 'none'; // Hide SMS tick on update to avoid spam
    } else {
        title.textContent = "Schedule Doctor Appointment";
        idField.value = "";
        smsGroup.style.display = 'block';
    }
    
    document.getElementById('appt-modal').classList.add('active');
}

function openMedModal(med = null) {
    document.getElementById('med-form').reset();
    const title = document.getElementById('med-modal-title');
    const idField = document.getElementById('med-id-field');
    
    if (med) {
        title.textContent = "Modify Medication Schedule";
        idField.value = med.id;
        document.getElementById('med-name').value = med.medicine_name;
        document.getElementById('med-dosage').value = med.dosage;
        document.getElementById('med-time').value = med.reminder_time;
        document.getElementById('med-frequency').value = med.frequency;
        document.getElementById('med-status').value = med.status;
        document.getElementById('med-sms-checkbox').checked = med.phone_reminder === 1;
    } else {
        title.textContent = "Add Medication Regimen";
        idField.value = "";
        document.getElementById('med-status').value = "Active";
        document.getElementById('med-sms-checkbox').checked = true;
    }
    
    document.getElementById('med-modal').classList.add('active');
}

function openNoteModal(note = null) {
    document.getElementById('note-form').reset();
    const title = document.getElementById('note-modal-title');
    const idField = document.getElementById('note-id-field');
    
    if (note) {
        title.textContent = "Modify Health Log Entry";
        idField.value = note.id;
        document.getElementById('note-title').value = note.title;
        document.getElementById('note-content').value = note.content;
    } else {
        title.textContent = "Record Health Log Entry";
        idField.value = "";
    }
    
    document.getElementById('note-modal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

/* --- SEARCH & FILTERS ENGINE --- */
function setupSearchFilters() {
    // 1. Appointments search and filters
    const triggerApptSearch = debounce(() => {
        apptCurrentPage = 1;
        loadAppointments();
    }, 400);
    
    document.getElementById('appt-search').addEventListener('input', triggerApptSearch);
    document.getElementById('appt-filter-start').addEventListener('change', triggerApptSearch);
    document.getElementById('appt-filter-end').addEventListener('change', triggerApptSearch);
    
    document.getElementById('appt-clear-filters').addEventListener('click', () => {
        document.getElementById('appt-search').value = "";
        document.getElementById('appt-filter-start').value = "";
        document.getElementById('appt-filter-end').value = "";
        apptCurrentPage = 1;
        loadAppointments();
    });
    
    // Appointment Pagination buttons
    document.getElementById('appt-prev-btn').addEventListener('click', () => {
        if (apptCurrentPage > 1) {
            apptCurrentPage--;
            renderAppointmentsTable();
        }
    });
    
    document.getElementById('appt-next-btn').addEventListener('click', () => {
        const maxPage = Math.ceil(appointments.length / apptPageSize);
        if (apptCurrentPage < maxPage) {
            apptCurrentPage++;
            renderAppointmentsTable();
        }
    });
    
    // 2. Medications status filters
    document.getElementById('med-status-filter').addEventListener('change', () => {
        loadMedications();
    });
    
    // 3. Health Notes Search
    const triggerNotesSearch = debounce(() => {
        loadNotes();
    }, 400);
    document.getElementById('notes-search').addEventListener('input', triggerNotesSearch);
}

/* --- DASHBOARD QUICK TRIGGERS & AI EXPORTS --- */
function setupDashboardActions() {
    // Click Generate in AI view
    document.getElementById('ai-generate-btn').addEventListener('click', () => {
        loadAISummary(true);
    });
    
    // Click Print in AI view
    document.getElementById('ai-print-btn').addEventListener('click', () => {
        window.print();
    });
    
    // Click Export in AI view
    document.getElementById('ai-export-btn').addEventListener('click', () => {
        const text = document.getElementById('ai-content-body').innerText;
        if (!text || text.includes('Click "Generate AI Summary"')) {
            Auth.showToast("No report text to export.", "warning");
            return;
        }
        
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `RK_Health_AI_Report_${new Date().toISOString().slice(0, 10)}.txt`;
        link.click();
        URL.revokeObjectURL(url);
    });
}

// Utilities
function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch (e) {
        return dateStr;
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
