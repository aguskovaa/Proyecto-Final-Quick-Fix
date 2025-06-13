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


window.addEventListener('click', (e) => {
    if (e.target === videoModal) {
        videoFrame.src = '';
        videoModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
      
        document.querySelectorAll('.nav-item').forEach(navItem => {
            navItem.classList.remove('active');
        });
        
        item.classList.add('active');
        
        console.log(`Navigating to: ${item.textContent}`);
    });
});