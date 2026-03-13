/**
 * Smart College Portal - Main JavaScript
 * Handles theme toggle, navigation, and interactive features
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initNavToggle();
    initUploadZones();
    initAutoHideFlash();
});

/**
 * Theme Toggle
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle?.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark'
            ? '<i class="fas fa-sun"></i>'
            : '<i class="fas fa-moon"></i>';
    }
}

/**
 * Mobile Navigation Toggle
 */
function initNavToggle() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    navToggle?.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!navToggle?.contains(e.target) && !navMenu?.contains(e.target)) {
            navMenu?.classList.remove('active');
        }
    });
}

/**
 * File Upload Zones
 */
function initUploadZones() {
    document.querySelectorAll('.upload-zone').forEach(zone => {
        const input = zone.querySelector('input[type="file"]');
        const preview = zone.querySelector('.upload-preview');

        // Drag and drop
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('dragover');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('dragover');

            if (e.dataTransfer.files.length && input) {
                input.files = e.dataTransfer.files;
                handleFilePreview(input, preview);
            }
        });

        // Click to select
        zone.addEventListener('click', () => input?.click());

        // File change
        input?.addEventListener('change', () => {
            handleFilePreview(input, preview);
        });
    });
}

function handleFilePreview(input, preview) {
    if (input.files && input.files[0] && preview) {
        const file = input.files[0];

        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }
}

/**
 * Auto-hide Flash Messages
 */
function initAutoHideFlash() {
    document.querySelectorAll('.flash-message').forEach(flash => {
        setTimeout(() => {
            flash.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });
}

/**
 * Chat Functions
 */
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const messages = document.getElementById('chatMessages');
    const query = input.value.trim();

    if (!query) return;

    // Add user message
    addChatMessage(query, 'user');
    input.value = '';

    // Show loading
    const loadingId = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = loadingId;
    loadingDiv.className = 'chat-message assistant';
    loadingDiv.innerHTML = `
        <div class="message-content-wrapper">
            <div class="jarvis-logo-small">J</div>
            <div class="loading">
                <div class="loading-spinner"></div>
                <span>Thinking...</span>
            </div>
        </div>
    `;
    messages.appendChild(loadingDiv);
    scrollToBottom();

    try {
        const response = await fetch('/chat/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        // Remove loading
        document.getElementById(loadingId)?.remove();

        // Add response
        addChatMessage(data.response || data.error, 'assistant');

        // Show related students if any
        if (data.students && data.students.length > 0) {
            addStudentCards(data.students);
        }

    } catch (error) {
        document.getElementById(loadingId)?.remove();
        addChatMessage('Sorry, an error occurred. Please try again.', 'assistant');
    }
}

function addChatMessage(content, type) {
    const messages = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = `chat-message ${type}`;
    
    if (type === 'assistant') {
        div.innerHTML = `
            <div class="message-content-wrapper">
                <div class="jarvis-logo-small">J</div>
                <div class="message-text">${formatMessage(content)}</div>
            </div>
        `;
    } else {
        div.innerHTML = `<div class="message-text">${formatMessage(content)}</div>`;
    }
    
    messages.appendChild(div);
    scrollToBottom();
}

function scrollToBottom() {
    const messages = document.getElementById('chatMessages');
    if (messages) {
        messages.scrollTo({
            top: messages.scrollHeight,
            behavior: 'smooth'
        });
    }
}

function formatMessage(text) {
    if (!text) return '';

    // Convert markdown to HTML
    let html = text
        // Escape HTML first
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // Headers
        .replace(/^### (.*$)/gm, '<h4 style="color: var(--primary); margin: 1rem 0 0.5rem; font-size: 1rem;">$1</h4>')
        .replace(/^## (.*$)/gm, '<h3 style="color: var(--primary); margin: 1rem 0 0.5rem; font-size: 1.1rem;">$1</h3>')
        .replace(/^# (.*$)/gm, '<h2 style="color: var(--primary); margin: 1rem 0 0.5rem; font-size: 1.25rem;">$1</h2>')
        // Bold and Italic
        .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.*?)\*\*/g, '<strong style="color: var(--text-primary);">$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        // Bullet points
        .replace(/^[\-\•] (.*$)/gm, '<li style="margin-left: 1.5rem; margin-bottom: 0.25rem;">$1</li>')
        .replace(/^\* (.*$)/gm, '<li style="margin-left: 1.5rem; margin-bottom: 0.25rem;">$1</li>')
        // Numbered lists
        .replace(/^\d+\. (.*$)/gm, '<li style="margin-left: 1.5rem; margin-bottom: 0.25rem;">$1</li>')
        // Horizontal rules
        .replace(/^---$/gm, '<hr style="border: none; border-top: 1px solid var(--border-color); margin: 1rem 0;">')
        .replace(/^___$/gm, '<hr style="border: none; border-top: 1px solid var(--border-color); margin: 1rem 0;">')
        // Code blocks
        .replace(/`([^`]+)`/g, '<code style="background: var(--bg-tertiary); padding: 0.15rem 0.4rem; border-radius: 4px; font-family: monospace; font-size: 0.9em;">$1</code>')
        // Line breaks
        .replace(/\n\n/g, '</p><p style="margin-bottom: 0.75rem;">')
        .replace(/\n/g, '<br>');

    // Wrap in paragraph
    html = '<p style="margin-bottom: 0.75rem;">' + html + '</p>';

    // Clean up empty paragraphs
    html = html.replace(/<p style="margin-bottom: 0.75rem;"><\/p>/g, '');

    return html;
}

function addStudentCards(students) {
    const messages = document.getElementById('chatMessages');
    const container = document.createElement('div');
    container.className = 'student-cards-container';
    container.style.cssText = 'display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1rem;';

    students.forEach(student => {
        container.innerHTML += `
            <a href="/student/${student.id}" class="card" style="flex: 1; min-width: 200px; max-width: 250px; text-decoration: none;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div class="student-avatar-placeholder" style="width: 40px; height: 40px; font-size: 1rem;">
                        ${student.name.charAt(0)}
                    </div>
                    <div>
                        <strong>${student.name}</strong>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">${student.department} - Year ${student.year}</div>
                    </div>
                </div>
            </a>
        `;
    });

    messages.appendChild(container);
    messages.scrollTop = messages.scrollHeight;
}

function useSuggestion(text) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = text;
        input.focus();
    }
}

/**
 * Job Assistant Functions
 */
async function analyzeJob() {
    const jobDesc = document.getElementById('jobDescription').value.trim();
    const resultsDiv = document.getElementById('jobResults');

    if (!jobDesc) {
        alert('Please enter a job description');
        return;
    }

    resultsDiv.innerHTML = '<div class="loading"><div class="loading-spinner"></div><span>Analyzing...</span></div>';

    try {
        const response = await fetch('/jobs/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_description: jobDesc })
        });

        const data = await response.json();

        if (data.error) {
            resultsDiv.innerHTML = `<div class="flash-message flash-error">${data.error}</div>`;
            return;
        }

        resultsDiv.innerHTML = `
            <div class="card">
                <h3><i class="fas fa-chart-bar"></i> Analysis Results</h3>
                <div style="white-space: pre-wrap; margin-top: 1rem;">${formatMessage(data.analysis)}</div>
            </div>
        `;

        if (data.suitable_students && data.suitable_students.length > 0) {
            let studentsHtml = '<div class="card" style="margin-top: 1rem;"><h3><i class="fas fa-users"></i> Matched Students</h3><div class="card-grid" style="margin-top: 1rem;">';

            data.suitable_students.forEach(student => {
                studentsHtml += `
                    <div class="card">
                        <div class="student-card" style="flex-direction: column; align-items: flex-start;">
                            <h4>${student.name}</h4>
                            <p>${student.department} - Year ${student.year}</p>
                            <div class="student-tags">
                                ${student.skills.slice(0, 3).map(s => `<span class="tag">${s}</span>`).join('')}
                            </div>
                            <div style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                                <button class="btn btn-sm btn-primary" onclick="generateResume(${student.id})">Resume</button>
                                <button class="btn btn-sm btn-secondary" onclick="generateCoverLetter(${student.id})">Cover Letter</button>
                            </div>
                        </div>
                    </div>
                `;
            });

            studentsHtml += '</div></div>';
            resultsDiv.innerHTML += studentsHtml;
        }

    } catch (error) {
        resultsDiv.innerHTML = `<div class="flash-message flash-error">Error: ${error.message}</div>`;
    }
}

async function generateResume(studentId) {
    const jobDesc = document.getElementById('jobDescription').value.trim();
    const resultsDiv = document.getElementById('jobResults');

    try {
        const response = await fetch('/jobs/generate-resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId, job_description: jobDesc })
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        // Show in modal or append to results
        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000;';
        modal.innerHTML = `
            <div class="card" style="max-width: 600px; max-height: 80vh; overflow-y: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3><i class="fas fa-file-alt"></i> Resume Points for ${data.student.name}</h3>
                    <button class="btn btn-sm btn-secondary" onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div style="white-space: pre-wrap;">${formatMessage(data.resume_points)}</div>
                <button class="btn btn-primary" style="margin-top: 1rem;" onclick="copyToClipboard(this.previousElementSibling.innerText)">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });

    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function generateCoverLetter(studentId) {
    const jobDesc = document.getElementById('jobDescription').value.trim();
    const company = prompt('Enter company name:') || 'the company';
    const role = prompt('Enter role/position:') || 'the position';

    try {
        const response = await fetch('/jobs/generate-cover-letter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                job_description: jobDesc,
                company_name: company,
                role: role
            })
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000;';
        modal.innerHTML = `
            <div class="card" style="max-width: 700px; max-height: 80vh; overflow-y: auto;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3><i class="fas fa-envelope"></i> Cover Letter for ${data.student.name}</h3>
                    <button class="btn btn-sm btn-secondary" onclick="this.parentElement.parentElement.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div style="white-space: pre-wrap;">${formatMessage(data.cover_letter)}</div>
                <button class="btn btn-primary" style="margin-top: 1rem;" onclick="copyToClipboard(this.previousElementSibling.innerText)">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
        `;
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });

    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    }).catch(err => {
        console.error('Copy failed', err);
    });
}

/**
 * Form Helpers
 */
function confirmDelete(name) {
    return confirm(`Are you sure you want to delete ${name}? This action cannot be undone.`);
}

// Handle Enter key in chat
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && e.target.id === 'chatInput' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
});
