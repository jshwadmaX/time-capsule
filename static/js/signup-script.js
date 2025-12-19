// Interactive Canvas Background (Same as landing page)
class InteractiveBackground {
    constructor() {
        this.canvas = document.getElementById('background-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: 0, y: 0 };
        this.animationFrame = null;

        this.init();
    }

    init() {
        this.resizeCanvas();
        this.createParticles();
        this.animate();

        window.addEventListener('resize', () => this.resizeCanvas());
        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.createParticles();
    }

    createParticles() {
        this.particles = [];
        const colors = [
            'rgba(255, 223, 0, 0.9)',
            'rgba(255, 215, 0, 0.8)',
            'rgba(255, 255, 200, 0.9)',
            'rgba(139, 163, 255, 0.7)',
            'rgba(184, 197, 255, 0.6)',
            'rgba(255, 200, 100, 0.8)',
        ];

        const particleCount = Math.floor((this.canvas.width * this.canvas.height) / 4000);

        for (let i = 0; i < particleCount; i++) {
            const x = Math.random() * this.canvas.width;
            const y = Math.random() * this.canvas.height;

            this.particles.push({
                x: x,
                y: y,
                baseX: x,
                baseY: y,
                vx: 0,
                vy: 0,
                size: Math.random() * 2.5 + 0.5,
                color: colors[Math.floor(Math.random() * colors.length)],
                angle: Math.random() * Math.PI * 2,
                speed: Math.random() * 0.3 + 0.1,
                twinkle: Math.random() * Math.PI * 2
            });
        }
    }

    drawSwirl(x, y, radius, rotation, alpha, color = 'sky') {
        this.ctx.save();
        this.ctx.translate(x, y);
        this.ctx.rotate(rotation);

        for (let i = 0; i < 5; i++) {
            this.ctx.beginPath();
            const offset = (i * Math.PI * 2) / 5;

            for (let angle = 0; angle < Math.PI * 3; angle += 0.05) {
                const r = radius * (1 - angle / (Math.PI * 3)) * 0.8;
                const px = Math.cos(angle * 1.5 + offset) * r;
                const py = Math.sin(angle * 1.5 + offset) * r;

                if (angle === 0) {
                    this.ctx.moveTo(px, py);
                } else {
                    this.ctx.lineTo(px, py);
                }
            }

            let gradient;
            if (color === 'gold') {
                gradient = this.ctx.createRadialGradient(0, 0, 0, 0, 0, radius);
                gradient.addColorStop(0, `rgba(255, 215, 0, ${alpha * 0.5})`);
                gradient.addColorStop(0.5, `rgba(255, 200, 100, ${alpha * 0.3})`);
                gradient.addColorStop(1, `rgba(255, 223, 0, 0)`);
            } else {
                gradient = this.ctx.createRadialGradient(0, 0, 0, 0, 0, radius);
                gradient.addColorStop(0, `rgba(139, 163, 255, ${alpha * 0.4})`);
                gradient.addColorStop(0.5, `rgba(107, 127, 215, ${alpha * 0.3})`);
                gradient.addColorStop(1, `rgba(74, 88, 153, 0)`);
            }

            this.ctx.strokeStyle = gradient;
            this.ctx.lineWidth = 3;
            this.ctx.stroke();
        }

        this.ctx.restore();
    }

    animate() {
        this.ctx.fillStyle = '#0a0e27';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        const bgGradient = this.ctx.createRadialGradient(
            this.canvas.width / 2, this.canvas.height / 3, 0,
            this.canvas.width / 2, this.canvas.height / 3, this.canvas.height
        );
        bgGradient.addColorStop(0, 'rgba(26, 31, 58, 0.5)');
        bgGradient.addColorStop(0.5, 'rgba(15, 20, 45, 0.7)');
        bgGradient.addColorStop(1, 'rgba(10, 14, 39, 0.9)');
        this.ctx.fillStyle = bgGradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        const time = Date.now() * 0.0003;

        this.drawSwirl(this.canvas.width * 0.15, this.canvas.height * 0.2, 200, time * 0.5, 0.6, 'sky');
        this.drawSwirl(this.canvas.width * 0.85, this.canvas.height * 0.25, 180, -time * 0.6, 0.5, 'sky');
        this.drawSwirl(this.canvas.width * 0.5, this.canvas.height * 0.15, 150, time * 0.8, 0.4, 'gold');
        this.drawSwirl(this.canvas.width * 0.3, this.canvas.height * 0.6, 160, -time * 0.4, 0.5, 'sky');
        this.drawSwirl(this.canvas.width * 0.7, this.canvas.height * 0.65, 140, time * 0.7, 0.4, 'sky');
        this.drawSwirl(this.canvas.width * 0.5, this.canvas.height * 0.8, 120, -time * 0.9, 0.3, 'gold');

        const distanceFromMouse = Math.hypot(
            this.mouse.x - this.canvas.width / 2,
            this.mouse.y - this.canvas.height / 2
        );

        if (distanceFromMouse < 600) {
            const alpha = 1 - distanceFromMouse / 600;
            this.drawSwirl(this.mouse.x, this.mouse.y, 150, time * 3, alpha * 0.8, 'gold');
            this.drawSwirl(this.mouse.x, this.mouse.y, 120, -time * 2, alpha * 0.6, 'sky');
        }

        this.particles.forEach(particle => {
            particle.angle += particle.speed * 0.015;
            const swirl = 40;
            const targetX = particle.baseX + Math.cos(particle.angle) * swirl;
            const targetY = particle.baseY + Math.sin(particle.angle) * swirl;

            const dx = this.mouse.x - particle.x;
            const dy = this.mouse.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const maxDistance = 250;

            if (distance < maxDistance) {
                const force = (maxDistance - distance) / maxDistance;
                const angle = Math.atan2(dy, dx);
                particle.vx += Math.cos(angle + Math.PI / 2) * force * 3;
                particle.vy += Math.sin(angle + Math.PI / 2) * force * 3;
                particle.vx += Math.cos(angle) * force * 1.5;
                particle.vy += Math.sin(angle) * force * 1.5;
            }

            particle.vx += (targetX - particle.x) * 0.03;
            particle.vy += (targetY - particle.y) * 0.03;
            particle.vx *= 0.92;
            particle.vy *= 0.92;
            particle.x += particle.vx;
            particle.y += particle.vy;

            particle.twinkle += 0.05;
            const twinkleAlpha = (Math.sin(particle.twinkle) + 1) / 2;

            const glowSize = particle.size * 3;
            const gradient = this.ctx.createRadialGradient(
                particle.x, particle.y, 0,
                particle.x, particle.y, glowSize
            );

            const baseAlpha = parseFloat(particle.color.match(/[\d.]+(?=\))/)[0]);
            gradient.addColorStop(0, particle.color);
            gradient.addColorStop(0.4, particle.color.replace(/[\d.]+(?=\))/, (twinkleAlpha * 0.6).toString()));
            gradient.addColorStop(1, particle.color.replace(/[\d.]+(?=\))/, '0'));

            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, glowSize, 0, Math.PI * 2);
            this.ctx.fill();

            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size * twinkleAlpha, 0, Math.PI * 2);
            this.ctx.fillStyle = particle.color;
            this.ctx.fill();
        });

        this.animationFrame = requestAnimationFrame(() => this.animate());
    }
}

// Create floating stars
function createFloatingStars() {
    const container = document.getElementById('floating-stars');

    for (let i = 0; i < 12; i++) {
        const star = document.createElement('div');
        star.className = 'floating-star';

        const size = Math.random() * 4 + 2;
        star.style.width = size + 'px';
        star.style.height = size + 'px';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';

        const duration = 3 + Math.random() * 3;
        const delay = Math.random() * 3;
        star.style.animation = `floatStar ${duration}s ease-in-out ${delay}s infinite`;

        container.appendChild(star);
    }
}

// Password Toggle
function setupPasswordToggle() {
    const toggleBtn = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');

    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
        });
    }
}

// Password Strength Checker
function checkPasswordStrength() {
    const passwordInput = document.getElementById('password');
    const strengthIndicator = document.getElementById('password-strength');

    if (passwordInput && strengthIndicator) {
        passwordInput.addEventListener('input', (e) => {
            const password = e.target.value;
            let strength = 0;

            if (password.length >= 8) strength++;
            if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
            if (password.match(/[0-9]/)) strength++;
            if (password.match(/[^a-zA-Z0-9]/)) strength++;

            strengthIndicator.className = 'password-strength';
            if (password.length === 0) {
                strengthIndicator.className = 'password-strength';
            } else if (strength <= 2) {
                strengthIndicator.className = 'password-strength weak';
            } else if (strength === 3) {
                strengthIndicator.className = 'password-strength medium';
            } else {
                strengthIndicator.className = 'password-strength strong';
            }
        });
    }
}

// Form Validation
function setupFormValidation() {
    const form = document.getElementById('signup-form');

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const terms = document.getElementById('terms').checked;

            // Validate password match
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            // Validate terms
            if (!terms) {
                alert('Please accept the Terms of Service and Privacy Policy');
                return;
            }

            // Validate password strength
            if (password.length < 8) {
                alert('Password must be at least 8 characters long');
                return;
            }

            // Success - In a real app, this would submit to a server
            console.log('Form submitted:', { name, email, password });

            // Show success message
            alert('Account created successfully! Welcome to CronoVault!');

            // Optionally redirect to login or dashboard
            // window.location.href = 'index.html';
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new InteractiveBackground();
    createFloatingStars();
    setupPasswordToggle();
    checkPasswordStrength();
    setupFormValidation();
});
