// Global functions that need to be accessible from HTML
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const themeIcon = document.querySelector('.theme-toggle i');
    themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

function hideModal() {
    const aboutModal = document.getElementById('aboutModal');
    if (aboutModal) {
        aboutModal.classList.remove('active');
    }
}

function hidePopup() {
    const popup = document.getElementById('popup');
    if (popup) {
        popup.style.display = 'none';
        popup.style.opacity = '0';
    }
}

function showTweets(word) {
    console.log('Showing tweets for word:', word);
    
    const popup = document.getElementById('popup');
    const title = document.getElementById('popup-title');
    const list = document.getElementById('popup-list');
    
    if (!popup || !title || !list) {
        console.error('Popup elements not found');
        return;
    }
    
    // Clear previous content
    list.innerHTML = '';
    
    // Set title
    title.textContent = `Recent tweets about ${word}`;
    
    // Show loading state
    list.innerHTML = '<li class="loading-item">Loading tweets...</li>';
    
    // Make sure popup is visible
    popup.style.display = 'block';
    popup.style.opacity = '1';
    
    // Get current language
    const languageSelect = document.querySelector('select[name="language"]');
    const language = languageSelect ? languageSelect.value : 'en';
    
    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrf_token"]');
    if (!csrfToken) {
        console.error('CSRF token not found');
        list.innerHTML = '<li class="error-item">Security token missing</li>';
        return;
    }
    
    console.log('Fetching tweets with:', { word, language });
    
    // Fetch tweets
    fetch('/fetch_tweets', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken.value
        },
        body: JSON.stringify({ 
            word: word,
            lang: language
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received data:', data);
        list.innerHTML = '';
        if (data.error) {
            list.innerHTML = `<li class="error-item">${data.error}</li>`;
        } else if (!data.tweets || data.tweets.length === 0) {
            list.innerHTML = '<li class="empty-item">No tweets found</li>';
        } else {
            displayTweets(data.tweets);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        list.innerHTML = `<li class="error-item">Error fetching tweets: ${error.message}</li>`;
    });
}

function displayTweets(tweets) {
    const list = document.getElementById('popup-list');
    if (!tweets || tweets.length === 0) {
        list.innerHTML = '<li class="empty-item">No tweets found</li>';
        return;
    }
    
    tweets.forEach(tweet => {
        const li = document.createElement('li');
        li.className = 'tweet-item';
        
        // Create tweet content div
        const tweetContent = document.createElement('div');
        tweetContent.className = 'tweet-content';
        
        // Safely add tweet text
        const tweetText = document.createElement('p');
        tweetText.textContent = tweet.text; // Use textContent to prevent XSS
        tweetContent.appendChild(tweetText);
        
        // Add metrics with null safety
        const metrics = tweet.metrics || {};
        const metricsDiv = document.createElement('div');
        metricsDiv.className = 'tweet-metrics';
        metricsDiv.innerHTML = `
            <span><i class="fas fa-retweet"></i> ${metrics.retweet_count || 0}</span>
            <span><i class="fas fa-heart"></i> ${metrics.like_count || 0}</span>
            <span><i class="fas fa-reply"></i> ${metrics.reply_count || 0}</span>
        `;
        tweetContent.appendChild(metricsDiv);
        
        // Format the date if available
        if (tweet.created_at) {
            const tweetDate = new Date(tweet.created_at);
            const formattedDate = tweetDate.toLocaleString();
            const dateDiv = document.createElement('div');
            dateDiv.className = 'tweet-date';
            dateDiv.textContent = formattedDate;
            tweetContent.appendChild(dateDiv);
        }
        
        li.appendChild(tweetContent);
        
        // Add link
        const link = document.createElement('a');
        link.href = tweet.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.className = 'tweet-link';
        link.innerHTML = '<i class="fas fa-external-link-alt"></i> View on Twitter';
        li.appendChild(link);
        
        list.appendChild(li);
    });
}

// Make showTweets available globally
window.showTweets = showTweets;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI elements
    const trendForm = document.getElementById('trendForm');
    const submitBtn = document.getElementById('submitBtn');
    const locationInput = document.querySelector('input[name="location"]');
    const errorDiv = document.getElementById('locationError');
    const aboutLink = document.getElementById('aboutLink');
    const aboutModal = document.getElementById('aboutModal');
    const wordcloudContainer = document.getElementById('wordcloud-container');
    const loadingOverlay = document.querySelector('.loading-overlay');

    // Initialize word cloud if data is available
    if (window.words_data && wordcloudContainer) {
        const width = wordcloudContainer.offsetWidth;
        const height = wordcloudContainer.offsetHeight;
        
        // Clear any existing SVG
        d3.select('#wordcloud-container').selectAll('svg').remove();
        
        // Create SVG container
        const svg = d3.select('#wordcloud-container')
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${width/2},${height/2})`);

        // Create word cloud layout
        const layout = d3.layout.cloud()
            .size([width, height])
            .words(window.words_data.map(d => ({
                text: d.word,
                size: d.font_size,
                type: d.type,
                volume: d.tweet_volume,
                color: d.color
            })))
            .padding(5)
            .rotate(() => Math.random() > 0.5 ? 0 : 90)
            .font('Inter')
            .fontSize(d => d.size)
            .on('end', draw);

        // Start the layout
        layout.start();

        // Draw the words
        function draw(words) {
            console.log('Drawing words:', words); // Debug log
            
            svg.selectAll('text')
                .data(words)
                .enter()
                .append('text')
                .style('font-size', d => `${d.size}px`)
                .style('font-family', 'Inter')
                .style('fill', d => d.color)
                .attr('text-anchor', 'middle')
                .attr('transform', d => `translate(${d.x},${d.y}) rotate(${d.rotate})`)
                .text(d => d.text)
                .style('cursor', 'pointer')
                .on('click', function(event, d) {
                    console.log('Word clicked:', d.text); // Debug log
                    showTweets(d.text);
                })
                .on('mouseover', function(event, d) {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .style('font-size', `${d.size * 1.1}px`);
                })
                .on('mouseout', function(event, d) {
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .style('font-size', `${d.size}px`);
                });
        }
    }

    // Form submission handling
    if (trendForm) {
        trendForm.addEventListener('submit', function(e) {
            if (!locationInput.value.trim()) {
                e.preventDefault();
                showError('Please enter a location');
                return;
            }
            
            if (locationInput.value.length > 100) {
                e.preventDefault();
                showError('Location name is too long');
                return;
            }
            
            hideError();
            submitBtn.classList.add('loading');
            if (loadingOverlay) {
                loadingOverlay.classList.add('active');
            }
        });
    }

    // Error handling
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.add('visible');
    }

    function hideError() {
        errorDiv.classList.remove('visible');
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        const themeIcon = document.querySelector('.theme-toggle i');
        if (themeIcon) {
            themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    // Modal handling
    if (aboutLink) {
        aboutLink.addEventListener('click', function(e) {
            e.preventDefault();
            if (aboutModal) {
                aboutModal.classList.add('active');
            }
        });
    }

    // Close modal when clicking outside
    if (aboutModal) {
        aboutModal.addEventListener('click', function(e) {
            if (e.target === aboutModal) {
                hideModal();
            }
        });
    }

    // Add click event listener for the close button
    const closeButtons = document.querySelectorAll('.close-button');
    closeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            // Check if this is the modal close button or popup close button
            const modal = this.closest('.modal');
            const popup = this.closest('.popup');
            
            if (modal) {
                hideModal();
            } else if (popup) {
                hidePopup();
            }
        });
    });

    // Close popup when clicking outside
    document.addEventListener('click', function(e) {
        const popup = document.getElementById('popup');
        if (popup && popup.style.display === 'block') {
            if (!popup.contains(e.target) && !e.target.closest('text')) {
                hidePopup();
            }
        }
    });

    // Prevent popup from closing when clicking inside it
    const popup = document.getElementById('popup');
    if (popup) {
        popup.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // Share functionality
    const shareBtn = document.getElementById('shareBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function() {
            if (navigator.share) {
                navigator.share({
                    title: document.title,
                    url: window.location.href
                }).catch(console.error);
            } else {
                // Fallback for browsers that don't support Web Share API
                navigator.clipboard.writeText(window.location.href)
                    .then(() => {
                        // Show feedback
                        const originalText = shareBtn.innerHTML;
                        shareBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        setTimeout(() => {
                            shareBtn.innerHTML = originalText;
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Failed to copy:', err);
                        // Fallback to old method if Clipboard API fails
                        const tempInput = document.createElement('input');
                        tempInput.value = window.location.href;
                        document.body.appendChild(tempInput);
                        tempInput.select();
                        document.execCommand('copy');
                        document.body.removeChild(tempInput);
                        const originalText = shareBtn.innerHTML;
                        shareBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                        setTimeout(() => {
                            shareBtn.innerHTML = originalText;
                        }, 2000);
                    });
            }
        });
    }

    // Copy link functionality
    const copyLinkBtn = document.getElementById('copyLinkBtn');
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', function() {
            navigator.clipboard.writeText(window.location.href)
                .then(() => {
                    // Show feedback
                    const originalText = copyLinkBtn.innerHTML;
                    copyLinkBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        copyLinkBtn.innerHTML = originalText;
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy:', err);
                    // Fallback to old method if Clipboard API fails
                    const tempInput = document.createElement('input');
                    tempInput.value = window.location.href;
                    document.body.appendChild(tempInput);
                    tempInput.select();
                    document.execCommand('copy');
                    document.body.removeChild(tempInput);
                    const originalText = copyLinkBtn.innerHTML;
                    copyLinkBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        copyLinkBtn.innerHTML = originalText;
                    }, 2000);
                });
        });
    }

    // Download functionality
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const svg = document.querySelector('#wordcloud-container svg');
            if (!svg) return;
            
            const serializer = new XMLSerializer();
            let source = serializer.serializeToString(svg);
            
            // Add namespace
            if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
                source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
            }
            
            // Add XML declaration
            source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
            
            // Create download link
            const url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'wordcloud.svg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }
    
    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        const themeIcon = document.querySelector('.theme-toggle i');
        if (themeIcon) {
            themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}); 