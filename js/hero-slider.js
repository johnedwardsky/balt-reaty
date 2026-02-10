function initHeroSlider() {
    const heroImgContainer = document.querySelector('.hero-img');
    if (!heroImgContainer) return;

    const images = heroImgContainer.querySelectorAll('.hero-slider-img');
    if (images.length <= 1) return;

    // Create dots container
    const dotsContainer = document.createElement('div');
    dotsContainer.className = 'hero-slider-dots';
    heroImgContainer.appendChild(dotsContainer);

    // Create dots
    images.forEach((_, idx) => {
        const dot = document.createElement('div');
        dot.className = 'hero-slider-dot' + (idx === 0 ? ' active' : '');
        dot.addEventListener('click', () => {
            goToSlide(idx);
            resetInterval();
        });
        dotsContainer.appendChild(dot);
    });

    const dots = dotsContainer.querySelectorAll('.hero-slider-dot');
    let currentIndex = 0;
    let isPaused = false;
    const intervalTime = 5000;
    let sliderInterval;

    function goToSlide(index) {
        images[currentIndex].classList.remove('active');
        dots[currentIndex].classList.remove('active');

        currentIndex = index;

        images[currentIndex].classList.add('active');
        dots[currentIndex].classList.add('active');
    }

    function showNextImage() {
        if (isPaused) return;
        let nextIndex = (currentIndex + 1) % images.length;
        goToSlide(nextIndex);
    }

    function startInterval() {
        sliderInterval = setInterval(showNextImage, intervalTime);
    }

    function resetInterval() {
        clearInterval(sliderInterval);
        startInterval();
    }

    startInterval();

    heroImgContainer.addEventListener('mouseenter', () => {
        isPaused = true;
    });

    heroImgContainer.addEventListener('mouseleave', () => {
        isPaused = false;
    });
}

document.addEventListener('DOMContentLoaded', initHeroSlider);
