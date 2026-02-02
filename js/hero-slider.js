function initHeroSlider() {
    const heroImgContainer = document.querySelector('.hero-img');
    if (!heroImgContainer) return;

    // We expect images to be inside a wrapper or just direct children
    // Let's assume we'll wrap them in .hero-slider-wrapper
    const images = heroImgContainer.querySelectorAll('.hero-slider-img');
    if (images.length <= 1) return;

    let currentIndex = 0;
    let isPaused = false;
    const intervalTime = 5000; // 5 seconds per slide

    function showNextImage() {
        if (isPaused) return;

        images[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % images.length;
        images[currentIndex].classList.add('active');
    }

    let sliderInterval = setInterval(showNextImage, intervalTime);

    heroImgContainer.addEventListener('mouseenter', () => {
        isPaused = true;
    });

    heroImgContainer.addEventListener('mouseleave', () => {
        isPaused = false;
    });
}

document.addEventListener('DOMContentLoaded', initHeroSlider);
