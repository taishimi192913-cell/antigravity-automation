document.addEventListener('DOMContentLoaded', () => {
    const cursor = document.getElementById('cursor-glow');
    const scrollRevealItems = document.querySelectorAll('.reveal-scroll');
    const heroTitle = document.querySelector('.hero h1');
    const heroPara = document.querySelector('.hero p');

    // Smooth Cursor Movement
    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateCursor() {
        const easing = 0.1;
        cursorX += (mouseX - cursorX) * easing;
        cursorY += (mouseY - cursorY) * easing;
        
        cursor.style.left = `${cursorX}px`;
        cursor.style.top = `${cursorY}px`;
        
        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // Intersection Observer for Scroll Animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    scrollRevealItems.forEach(item => {
        observer.observe(item);
    });

    // Hero Entrance Animations
    setTimeout(() => {
        if (heroTitle) {
            heroTitle.style.opacity = '1';
            heroTitle.style.transform = 'translateY(0)';
        }
        if (heroPara) {
            heroPara.style.opacity = '0.6';
            heroPara.style.transform = 'translateY(0)';
        }
    }, 300);

    // Hover effect for gallery items scale & rotation (optional flair)
    document.querySelectorAll('.gallery-item').forEach(item => {
        item.addEventListener('mousemove', (e) => {
            const rect = item.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;
            
            const img = item.querySelector('.img-container');
            if (img) {
                img.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
            }
        });
        
        item.addEventListener('mouseleave', () => {
            const img = item.querySelector('.img-container');
            if (img) {
                img.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
            }
        });
    });
});
