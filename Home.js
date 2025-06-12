// Video Modal functionality
const playButton = document.getElementById('playButton');
const videoModal = document.getElementById('videoModal');
const closeModal = document.getElementById('closeModal');
const videoFrame = document.getElementById('videoFrame');

playButton.addEventListener('click', () => {
    videoFrame.src = 'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1';
    videoModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
});

closeModal.addEventListener('click', () => {
    videoFrame.src = '';
    videoModal.style.display = 'none';
    document.body.style.overflow = 'auto';
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === videoModal) {
        videoFrame.src = '';
        videoModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

// Smooth scroll for navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all items
        document.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.classList.remove('active');
        });
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // Here you would typically scroll to the corresponding section
        // For demo purposes, we'll just log it
        console.log(`Navigating to: ${item.textContent}`);
    });
});