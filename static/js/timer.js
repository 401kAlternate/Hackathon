// Timer functionality for IDE

function formatTime(seconds) {
    if (seconds <= 0) return '00:00:00';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return [hours.toString().padStart(2, '0'), minutes.toString().padStart(2, '0'), secs.toString().padStart(2, '0')].join(':');
}

function updateTimers() {
    const now = new Date().getTime();
    document.querySelectorAll('[data-bidding-deadline]').forEach(element => {
        const deadline = parseInt(element.dataset.biddingDeadline);
        const remaining = Math.max(0, Math.floor((deadline - now) / 1000));
        element.textContent = formatTime(remaining);
        element.classList.toggle('urgent', remaining > 0 && remaining < 3600);
    });
    document.querySelectorAll('[data-writing-deadline]').forEach(element => {
        const deadline = parseInt(element.dataset.writingDeadline);
        const remaining = Math.max(0, Math.floor((deadline - now) / 1000));
        element.textContent = formatTime(remaining);
        element.classList.toggle('urgent', remaining > 0 && remaining < 3600);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    updateTimers();
    setInterval(updateTimers, 1000);
});

window.HackathonTimer = { formatTime, updateTimers };