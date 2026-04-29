// ==================== Theme Toggle ====================
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const appContainer = document.querySelector('.app-container');
    const sunIcon = themeToggle?.querySelector('.sun-icon');
    const moonIcon = themeToggle?.querySelector('.moon-icon');
    
    if (themeToggle) {
        // Initialize theme from localStorage or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        appContainer.setAttribute('data-theme', savedTheme);
        updateThemeIcons(savedTheme);
        
        // Theme toggle event listener
        themeToggle.addEventListener('click', function() {
            const currentTheme = appContainer.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            appContainer.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcons(newTheme);
            
            // Send preference to server
            fetch('/settings/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ theme: newTheme })
            }).catch(() => {
                // Silently fail - theme is updated locally
            });
        });
    }
    
    function updateThemeIcons(theme) {
        if (sunIcon && moonIcon) {
            if (theme === 'dark') {
                sunIcon.style.display = 'none';
                moonIcon.style.display = 'block';
            } else {
                sunIcon.style.display = 'block';
                moonIcon.style.display = 'none';
            }
        }
    }
});

// ==================== Form Validation ====================
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('.form-control[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// ==================== Color Picker ====================
const colorPickers = document.querySelectorAll('.color-picker');
colorPickers.forEach(picker => {
    picker.addEventListener('change', function() {
        const valueDisplay = this.parentElement.querySelector('.color-value');
        if (valueDisplay) {
            valueDisplay.textContent = this.value;
        }
    });
});

// ==================== Task Interactions ====================

/**
 * Toggle task completion status
 */
function toggleTask(taskId) {
    fetch(`/task/${taskId}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
            if (taskCard) {
                const checkbox = taskCard.querySelector('.task-complete');
                if (checkbox) {
                    checkbox.checked = data.is_completed;
                }
                taskCard.classList.toggle('completed');
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

/**
 * Toggle task important status
 */
function toggleImportant(taskId) {
    fetch(`/task/${taskId}/important`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const btn = event.target.closest('.task-important-btn');
            if (btn) {
                btn.textContent = data.is_important ? '⭐' : '☆';
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

/**
 * Mark task as complete
 */
function completeTask(taskId) {
    const confirmed = confirm('Mark this task as complete?');
    if (confirmed) {
        toggleTask(taskId);
    }
}

/**
 * Delete task with confirmation
 */
function deleteTaskWithConfirmation(taskId) {
    const confirmed = confirm('Are you sure you want to delete this task? This action cannot be undone.');
    if (confirmed) {
        const form = document.querySelector(`form[action*="/task/${taskId}/delete"]`);
        if (form) {
            form.submit();
        }
    }
}

// ==================== Subtask Interactions ====================

/**
 * Toggle subtask completion
 */
function toggleSubtask(subtaskId) {
    fetch(`/subtask/${subtaskId}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const subtaskItem = document.querySelector(`[data-subtask-id="${subtaskId}"]`);
            if (subtaskItem) {
                const checkbox = subtaskItem.querySelector('.subtask-check');
                if (checkbox) {
                    checkbox.checked = data.is_completed;
                }
                subtaskItem.classList.toggle('completed');
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

/**
 * Delete subtask with confirmation
 */
function deleteSubtask(subtaskId) {
    const confirmed = confirm('Delete this subtask?');
    if (!confirmed) return;
    
    fetch(`/subtask/${subtaskId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const subtaskItem = document.querySelector(`[data-subtask-id="${subtaskId}"]`);
            if (subtaskItem) {
                subtaskItem.style.opacity = '0';
                setTimeout(() => subtaskItem.remove(), 300);
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

/**
 * Add subtask
 */
function addSubtask(taskId) {
    const input = document.getElementById('subtask-title');
    const title = input?.value.trim();
    
    if (!title) {
        alert('Please enter a subtask title');
        return;
    }
    
    fetch(`/task/${taskId}/subtask/add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: title })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (input) input.value = '';
            // Could add subtask to DOM dynamically here
            location.reload();
        } else {
            alert('Error adding subtask: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding subtask');
    });
}

/**
 * Toggle add subtask form visibility
 */
function toggleAddSubtask() {
    const form = document.getElementById('add-subtask-form');
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
        if (form.style.display === 'block') {
            const input = document.getElementById('subtask-title');
            if (input) input.focus();
        }
    }
}

// ==================== Category Interactions ====================

/**
 * Delete category with confirmation
 */
function deleteCategory(categoryId) {
    const confirmed = confirm(
        'Are you sure you want to delete this category? ' +
        'Tasks in this category will remain but be uncategorized.'
    );
    if (confirmed) {
        const form = document.querySelector(`form[action*="/category/${categoryId}/delete"]`);
        if (form) {
            form.submit();
        }
    }
}

// ==================== Tag Interactions ====================

/**
 * Delete tag with confirmation
 */
function deleteTag(tagId) {
    const confirmed = confirm('Delete this tag?');
    if (confirmed) {
        const form = document.querySelector(`form[action*="/tag/${tagId}/delete"]`);
        if (form) {
            form.submit();
        }
    }
}

/**
 * Add tag to task
 */
function addTagToTask(taskId, tagId) {
    fetch(`/task/${taskId}/tag/${tagId}/add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Tag added successfully');
        }
    })
    .catch(error => console.error('Error:', error));
}

/**
 * Remove tag from task
 */
function removeTagFromTask(taskId, tagId) {
    fetch(`/task/${taskId}/tag/${tagId}/remove`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Tag removed successfully');
        }
    })
    .catch(error => console.error('Error:', error));
}

// ==================== Date Picker ====================

/**
 * Initialize date pickers
 */
function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
    dateInputs.forEach(input => {
        // Set default to current date/time
        if (!input.value) {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            
            input.value = `${year}-${month}-${day}T${hours}:${minutes}`;
        }
    });
}

// ==================== Search and Filter ====================

/**
 * Debounce function for search
 */
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

/**
 * Handle search input changes
 */
const searchInput = document.querySelector('.search-box input[name="search"]');
if (searchInput) {
    searchInput.addEventListener('input', debounce(function() {
        // Could implement live search here
    }, 500));
}

// ==================== Keyboard Shortcuts ====================

/**
 * Initialize keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N: New task
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        const newTaskBtn = document.querySelector('a[href*="/task/new"]');
        if (newTaskBtn) {
            newTaskBtn.click();
        }
    }
    
    // Ctrl/Cmd + F: Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-box input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape: Close modals/forms
    if (e.key === 'Escape') {
        const modal = document.querySelector('#add-subtask-form');
        if (modal && modal.style.display !== 'none') {
            modal.style.display = 'none';
        }
    }
});

// ==================== Notification System ====================

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 3000) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(alert, mainContent.firstChild);
        
        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.3s';
                setTimeout(() => alert.remove(), 300);
            }, duration);
        }
        
        // Close button
        const closeBtn = alert.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.remove();
            });
        }
    }
}

// ==================== Utility Functions ====================

/**
 * Format date to readable string
 */
function formatDate(date) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-US', options);
}

/**
 * Format time to readable string
 */
function formatTime(date) {
    const options = { hour: '2-digit', minute: '2-digit' };
    return new Date(date).toLocaleTimeString('en-US', options);
}

/**
 * Get time remaining until a date
 */
function getTimeRemaining(dueDate) {
    const now = new Date();
    const due = new Date(dueDate);
    const diff = due - now;
    
    if (diff < 0) return 'Overdue';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} remaining`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} remaining`;
    return 'Due soon';
}

// ==================== Initialize on Load ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeDatePickers();
    
    // Initialize tooltips (if using a tooltip library)
    // You can add Bootstrap tooltips or similar here
});

// ==================== Smooth Transitions ====================
document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to page elements
    const elements = document.querySelectorAll('.task-card, .stat-card, .category-card');
    elements.forEach((el, index) => {
        el.style.animation = `fadeIn 0.3s ease forwards`;
        el.style.animationDelay = `${index * 0.05}s`;
    });
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

// ==================== Export Functions ====================

/**
 * Export tasks as CSV
 */
function exportAsCSV() {
    fetch('/api/tasks/export')
        .then(response => response.json())
        .then(tasks => {
            let csv = 'Title,Description,Priority,Due Date,Completed,Category\n';
            
            tasks.forEach(task => {
                const row = [
                    `"${task.title.replace(/"/g, '""')}"`,
                    `"${(task.description || '').replace(/"/g, '""')}"`,
                    task.priority,
                    task.due_date || '',
                    task.is_completed ? 'Yes' : 'No',
                    task.category || ''
                ];
                csv += row.join(',') + '\n';
            });
            
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tasks-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error exporting tasks', 'danger');
        });
}

/**
 * Export tasks as JSON
 */
function exportAsJSON() {
    fetch('/api/tasks/export')
        .then(response => response.json())
        .then(tasks => {
            const json = JSON.stringify(tasks, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tasks-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error exporting tasks', 'danger');
        });
}
