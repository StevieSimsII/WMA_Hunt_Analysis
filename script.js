// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update active nav link
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    // Update active nav link on scroll
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        const scrollPosition = window.scrollY + 100;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });

    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinksContainer = document.querySelector('.nav-links');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            navLinksContainer.classList.toggle('active');
        });
    }

    // Initialize ranking tabs
    initializeRankingTabs();
    
    // Initialize calendar views
    initializeCalendarViews();
    
    // Add scroll animations
    addScrollAnimations();
});

// Utility function for smooth scrolling to sections
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Rankings tab functionality
function initializeRankingTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const rankingCategories = document.querySelectorAll('.ranking-category');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const category = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            showRankingCategory(category);
        });
    });
}

function showRankingCategory(category) {
    // Hide all categories
    const categories = document.querySelectorAll('.ranking-category');
    categories.forEach(cat => cat.classList.remove('active'));
    
    // Show selected category
    const targetCategory = document.getElementById(`${category}-rankings`);
    if (targetCategory) {
        targetCategory.classList.add('active');
    }
    
    // Update active tab
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Find and activate the correct tab
    tabs.forEach(tab => {
        const tabText = tab.textContent.toLowerCase();
        if ((category === 'gun' && tabText.includes('gun')) ||
            (category === 'archery' && tabText.includes('archery')) ||
            (category === 'primitive' && tabText.includes('primitive')) ||
            (category === 'group' && tabText.includes('group'))) {
            tab.classList.add('active');
        }
    });
}

// Calendar view functionality
function initializeCalendarViews() {
    const calendarButtons = document.querySelectorAll('.calendar-btn');
    const calendarViews = document.querySelectorAll('.calendar-view');

    calendarButtons.forEach(button => {
        button.addEventListener('click', function() {
            const view = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            showCalendarView(view);
        });
    });
}

function showCalendarView(view) {
    // Hide all views
    const views = document.querySelectorAll('.calendar-view');
    views.forEach(v => v.classList.remove('active'));
    
    // Show selected view
    const targetView = document.getElementById(`${view}-view`);
    if (targetView) {
        targetView.classList.add('active');
    }
    
    // Update active button
    const buttons = document.querySelectorAll('.calendar-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Find and activate the correct button
    buttons.forEach(btn => {
        const btnText = btn.textContent.toLowerCase();
        if ((view === 'timeline' && btnText.includes('timeline')) ||
            (view === 'monthly' && btnText.includes('monthly')) ||
            (view === 'moon' && btnText.includes('moon'))) {
            btn.classList.add('active');
        }
    });
}

// Scroll animations
function addScrollAnimations() {
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

    // Observe cards and items for animation
    const animatedElements = document.querySelectorAll('.strategy-card, .ranking-item, .about-card, .analysis-card');
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

// Hunt block hover effects for timeline
document.addEventListener('DOMContentLoaded', function() {
    const huntBlocks = document.querySelectorAll('.hunt-block');
    huntBlocks.forEach(block => {
        block.addEventListener('mouseenter', function() {
            const huntInfo = this.querySelector('.hunt-info');
            if (huntInfo) {
                huntInfo.style.transform = 'scale(1.05)';
            }
        });
        
        block.addEventListener('mouseleave', function() {
            const huntInfo = this.querySelector('.hunt-info');
            if (huntInfo) {
                huntInfo.style.transform = 'scale(1)';
            }
        });
    });
});

// Moon phase tooltip functionality
function showMoonPhaseInfo(phase, date) {
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'moon-tooltip';
    tooltip.innerHTML = `
        <div class="tooltip-content">
            <h4>${phase}</h4>
            <p>${date}</p>
            <small>Optimal deer movement conditions</small>
        </div>
    `;
    
    // Add tooltip styles
    tooltip.style.cssText = `
        position: fixed;
        background: var(--bg-dark);
        color: var(--text-white);
        padding: var(--space-md);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    // Position and show tooltip
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
    
    // Remove tooltip after delay
    setTimeout(() => {
        tooltip.style.opacity = '0';
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
        }, 300);
    }, 3000);
}

// Add click events for interactive elements
document.addEventListener('DOMContentLoaded', function() {
    // Strategy card click effects
    const strategyCards = document.querySelectorAll('.strategy-card');
    strategyCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add click animation
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });

    // Ranking item click effects
    const rankingItems = document.querySelectorAll('.ranking-item');
    rankingItems.forEach(item => {
        item.addEventListener('click', function() {
            // Highlight selected item
            rankingItems.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
});

// Search functionality (future enhancement)
function searchHunts(query) {
    const searchResults = [];
    const allHunts = document.querySelectorAll('.strategy-card, .ranking-item');
    
    allHunts.forEach(hunt => {
        const text = hunt.textContent.toLowerCase();
        if (text.includes(query.toLowerCase())) {
            searchResults.push(hunt);
        }
    });
    
    return searchResults;
}

// Export functionality for sharing
function exportStrategy() {
    const strategyData = {
        timestamp: new Date().toISOString(),
        strategy: 'Optimal 5-Hunt Application Strategy',
        hunts: [
            {
                rank: 1,
                type: 'Group Gun Hunt',
                location: 'Phil Bryant (Backwoods Unit)',
                dates: 'November 19-23, 2025',
                score: '3.26/5.0'
            },
            {
                rank: 2,
                type: 'Peak Rut Archery',
                location: 'Phil Bryant (Goose Lake Unit)',
                dates: 'January 1-4, 2026',
                score: '3.82/5.0'
            },
            {
                rank: 3,
                type: 'Optimal Conditions Archery',
                location: 'Phil Bryant (Goose Lake Unit)',
                dates: 'December 18-21, 2025',
                score: '4.04/5.0'
            },
            {
                rank: 4,
                type: 'Primitive Weapon',
                location: 'Mahannah WMA',
                dates: 'November 20-21, 2025',
                score: '3.1/5.0'
            },
            {
                rank: 5,
                type: 'Gun Hunt Backup',
                location: 'Mahannah WMA',
                dates: 'December 21-22, 2025',
                score: '3.4/5.0'
            }
        ]
    };
    
    const dataStr = JSON.stringify(strategyData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'wma-hunt-strategy.json';
    link.click();
    
    URL.revokeObjectURL(url);
}

// Print functionality
function printStrategy() {
    const printWindow = window.open('', '_blank');
    const strategySection = document.getElementById('strategy');
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>WMA Hunt Strategy - Print</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .strategy-card { margin-bottom: 20px; padding: 15px; border: 1px solid #ccc; }
                .card-title { font-weight: bold; color: #2c3e50; }
                .card-details { margin: 10px 0; }
                .detail-item { margin: 5px 0; }
            </style>
        </head>
        <body>
            <h1>Mississippi WMA Hunt Analysis - Optimal Strategy</h1>
            ${strategySection.innerHTML}
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
}

// Theme toggle (future enhancement)
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

// Load saved theme
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
});

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    // Arrow key navigation for tabs
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        const activeTab = document.querySelector('.tab-btn.active, .calendar-btn.active');
        if (activeTab) {
            const tabs = Array.from(activeTab.parentNode.children);
            const currentIndex = tabs.indexOf(activeTab);
            let newIndex;
            
            if (e.key === 'ArrowLeft') {
                newIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
            } else {
                newIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
            }
            
            tabs[newIndex].click();
        }
    }
});

// Performance optimization - lazy loading for images (if added)
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}
