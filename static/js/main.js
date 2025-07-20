// Sound Effects
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

function playSound(frequency, duration, type = 'sine') {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
    oscillator.type = type;
    
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);
}

// Sound Controls
let isMuted = false;
const soundToggle = document.getElementById('soundToggle');
const soundIcon = document.querySelector('.sound-icon');

if (soundToggle) {
    soundToggle.addEventListener('click', function() {
        isMuted = !isMuted;
        soundToggle.classList.toggle('muted');
        soundIcon.textContent = isMuted ? '🔇' : '🔊';
        
        if (!isMuted) {
            playSound(800, 0.1);
        }
    });
}

// Quiz Navigation Logic
document.addEventListener('DOMContentLoaded', function() {
    const quizForm = document.getElementById('personality-quiz');
    const questions = document.querySelectorAll('.question');
    const nextButton = document.querySelector('.next-button');
    const prevButton = document.querySelector('.prev-button');
    const submitButton = document.querySelector('.submit-button');
    const currentQuestionSpan = document.querySelector('.current-question');
    
    let currentQuestionIndex = 0;
    const totalQuestions = questions.length;
    
    // Initialize quiz
    updateQuestionDisplay();
    updateNavigationButtons();
    
    // Next button click handler
    if (nextButton) {
        nextButton.addEventListener('click', function() {
            if (currentQuestionIndex < totalQuestions - 1) {
                // Check if current question is answered
                const currentQuestion = questions[currentQuestionIndex];
                const selectedOption = currentQuestion.querySelector('input[type="radio"]:checked');
                
                if (selectedOption) {
                    currentQuestionIndex++;
                    updateQuestionDisplay();
                    updateNavigationButtons();
                } else {
                    // Show error or highlight that an option must be selected
                    highlightUnansweredQuestion();
                }
            }
        });
    }
    
    // Previous button click handler
    if (prevButton) {
        prevButton.addEventListener('click', function() {
            if (currentQuestionIndex > 0) {
                currentQuestionIndex--;
                updateQuestionDisplay();
                updateNavigationButtons();
            }
        });
    }
    
    // Radio button change handler
    questions.forEach(question => {
        const radioButtons = question.querySelectorAll('input[type="radio"]');
        radioButtons.forEach(radio => {
            radio.addEventListener('change', function() {
                // Play selection sound
                if (!isMuted) {
                    playSound(600, 0.2);
                }
                
                // Auto-advance to next question after a short delay
                setTimeout(() => {
                    if (currentQuestionIndex < totalQuestions - 1) {
                        currentQuestionIndex++;
                        updateQuestionDisplay();
                        updateNavigationButtons();
                    }
                }, 500);
            });
        });
    });
    
    function updateQuestionDisplay() {
        questions.forEach((question, index) => {
            if (index === currentQuestionIndex) {
                question.classList.add('active');
            } else {
                question.classList.remove('active');
            }
        });
        
        if (currentQuestionSpan) {
            currentQuestionSpan.textContent = currentQuestionIndex + 1;
        }
    }
    
    function updateNavigationButtons() {
        // Update previous button
        if (prevButton) {
            prevButton.disabled = currentQuestionIndex === 0;
        }
        
        // Update next button and submit button
        if (currentQuestionIndex === totalQuestions - 1) {
            if (nextButton) nextButton.style.display = 'none';
            if (submitButton) submitButton.style.display = 'inline-block';
        } else {
            if (nextButton) nextButton.style.display = 'inline-block';
            if (submitButton) submitButton.style.display = 'none';
        }
    }
    
    function highlightUnansweredQuestion() {
        const currentQuestion = questions[currentQuestionIndex];
        const options = currentQuestion.querySelectorAll('.option-content');
        
        // Play error sound
        if (!isMuted) {
            playSound(200, 0.3, 'sawtooth');
        }
        
        options.forEach(option => {
            option.style.animation = 'shake 0.5s ease-in-out';
        });
        
        // Remove animation after it completes
        setTimeout(() => {
            options.forEach(option => {
                option.style.animation = '';
            });
        }, 500);
    }
});

// Add shake animation to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Parallax effect for hero background
document.addEventListener('DOMContentLoaded', function() {
    const heroBackground = document.querySelector('.hero-background');
    
    if (heroBackground) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroBackground.style.transform = `translateY(${rate}px)`;
        });
    }
});

// Movie card hover effects
document.addEventListener('DOMContentLoaded', function() {
    const movieCards = document.querySelectorAll('.movie-card');
    
    movieCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Loading animation for API calls
function showLoading(element) {
    element.style.opacity = '0.6';
    element.style.pointerEvents = 'none';
    
    const loadingSpinner = document.createElement('div');
    loadingSpinner.className = 'loading-spinner';
    loadingSpinner.innerHTML = `
        <div class="spinner"></div>
        <p>Finding your perfect movies...</p>
    `;
    
    element.appendChild(loadingSpinner);
}

function hideLoading(element) {
    element.style.opacity = '1';
    element.style.pointerEvents = 'auto';
    
    const loadingSpinner = element.querySelector('.loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.remove();
    }
}

// Add loading spinner styles
const loadingStyle = document.createElement('style');
loadingStyle.textContent = `
    .loading-spinner {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
        z-index: 10;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-top: 4px solid #ff6b6b;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(loadingStyle);

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const quizForm = document.getElementById('personality-quiz');
    
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            const questions = document.querySelectorAll('.question');
            let allAnswered = true;
            
            questions.forEach(question => {
                const radioButtons = question.querySelectorAll('input[type="radio"]');
                const answered = Array.from(radioButtons).some(radio => radio.checked);
                
                if (!answered) {
                    allAnswered = false;
                    question.style.border = '2px solid #ff6b6b';
                } else {
                    question.style.border = 'none';
                }
            });
            
            if (!allAnswered) {
                e.preventDefault();
                alert('Please answer all questions before submitting.');
            }
        });
    }
});

// Smooth transitions for page navigation
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add fade out effect before navigation
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.3s ease';
            
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 300);
        });
    });
});

// Intersection Observer for animations
document.addEventListener('DOMContentLoaded', function() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.movie-card, .feature, .trait-tag');
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        el.style.setProperty('--card-index', index);
        observer.observe(el);
    });
    
    // Handle loading animation
    const loadingAnimation = document.getElementById('loadingAnimation');
    if (loadingAnimation) {
        // Hide loading after 3 seconds
        setTimeout(() => {
            loadingAnimation.classList.add('hidden');
            setTimeout(() => {
                loadingAnimation.style.display = 'none';
            }, 500);
        }, 3000);
    }
    
    // Handle trailer buttons
    const trailerButtons = document.querySelectorAll('.play-trailer-btn');
    trailerButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const movieTitle = this.closest('.movie-card').dataset.movie;
            
            // Play click sound
            if (!isMuted) {
                playSound(800, 0.2);
            }
            
            // Show trailer modal (placeholder for now)
            showTrailerModal(movieTitle);
        });
    });
});

// Trailer Modal
function showTrailerModal(movieTitle) {
    const modal = document.createElement('div');
    modal.className = 'trailer-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${movieTitle} - Trailer</h3>
                <button class="close-modal">×</button>
            </div>
            <div class="modal-body">
                <p>Trailer for ${movieTitle} would play here.</p>
                <p>In a real implementation, this would embed a YouTube video or similar.</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal functionality
    const closeBtn = modal.querySelector('.close-modal');
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
} 