// wordcloud-d3.js

document.addEventListener('DOMContentLoaded', function() {
    if (!window.wordsData) {
        // Build wordsData from DOM if not present (fallback)
        const container = document.getElementById('wordcloud-svg-container');
        if (!container) return;
        window.wordsData = [];
    }
    const svgContainer = document.getElementById('wordcloud-svg-container');
    const tooltip = document.getElementById('tooltip');
    const filterHashtags = document.getElementById('filterHashtags');
    const filterKeywords = document.getElementById('filterKeywords');
    const sortWords = document.getElementById('sortWords');
    const searchWord = document.getElementById('searchWord');
    const languageSelect = document.getElementById('language');

    // Get words_data from Jinja context
    let wordsData = window.words_data || [];
    if (!wordsData.length && window.wordsData) wordsData = window.wordsData;

    // Helper: filter/sort/search
    function getFilteredWords() {
        let filtered = wordsData.slice();
        if (!filterHashtags.checked) filtered = filtered.filter(w => w.type !== 'hashtag');
        if (!filterKeywords.checked) filtered = filtered.filter(w => w.type !== 'keyword');
        const query = searchWord.value.trim().toLowerCase();
        if (query) filtered = filtered.filter(w => w.word.toLowerCase().includes(query));
        if (sortWords.value === 'freq') filtered.sort((a, b) => b.tweet_volume - a.tweet_volume);
        else if (sortWords.value === 'alpha') filtered.sort((a, b) => a.word.localeCompare(b.word));
        else if (sortWords.value === 'random') filtered = d3.shuffle(filtered);
        return filtered;
    }

    // Render word cloud
    function renderWordCloud() {
        svgContainer.innerHTML = '';
        const width = svgContainer.offsetWidth || 800;
        const height = 400;
        const words = getFilteredWords();
        if (!words.length) return;
        d3.layout.cloud()
            .size([width, height])
            .words(words.map(d => ({
                text: d.word,
                size: d.font_size,
                color: d.color,
                tweet_volume: d.tweet_volume,
                type: d.type,
                orientation: d.orientation,
            })))
            .padding(5)
            .rotate(d => d.orientation === 'vertical' ? 90 : 0)
            .font('Inter, Arial, sans-serif')
            .fontSize(d => d.size)
            .on('end', draw)
            .start();

        function draw(words) {
            const svg = d3.select(svgContainer)
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .attr('viewBox', `0 0 ${width} ${height}`)
                .attr('role', 'img')
                .attr('aria-label', 'Word cloud of trending topics');
            const g = svg.append('g')
                .attr('transform', `translate(${width/2},${height/2})`);
            g.selectAll('text')
                .data(words)
                .enter().append('text')
                .attr('class', d => `word ${d.type}`)
                .attr('text-anchor', 'middle')
                .attr('font-size', d => d.size)
                .attr('fill', d => d.color)
                .attr('aria-label', d => `${d.text}: ${d.tweet_volume} tweets`)
                .attr('tabindex', 0)
                .attr('style', 'cursor:pointer; font-weight:600;')
                .attr('transform', d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
                .text(d => d.text)
                .on('mouseover', function(e, d) {
                    tooltip.innerHTML = `<strong>${d.text}</strong><br>${d.tweet_volume} tweets`;
                    tooltip.style.display = 'block';
                })
                .on('mousemove', function(e) {
                    tooltip.style.left = (e.pageX + 12) + 'px';
                    tooltip.style.top = (e.pageY - 24) + 'px';
                })
                .on('mouseout', function() {
                    tooltip.style.display = 'none';
                })
                .on('click', function(e, d) {
                    // Simulate click for popup (reuse script.js logic)
                    const event = new CustomEvent('wordcloud-click', { detail: { word: d.text } });
                    window.dispatchEvent(event);
                })
                .on('keydown', function(e, d) {
                    if (e.key === 'Enter' || e.key === ' ') {
                        const event = new CustomEvent('wordcloud-click', { detail: { word: d.text } });
                        window.dispatchEvent(event);
                    }
                });
        }
    }

    // Listen for filter/sort/search changes
    [filterHashtags, filterKeywords, sortWords, searchWord].forEach(el => {
        el.addEventListener('input', renderWordCloud);
        el.addEventListener('change', renderWordCloud);
    });

    // Listen for word click to trigger popup
    window.addEventListener('wordcloud-click', function(e) {
        const word = e.detail.word;
        // Find the corresponding DOM element in the SVG
        // Simulate click on the first matching .word in the SVG
        const svgWord = svgContainer.querySelector('text.word');
        if (svgWord) {
            // Use the existing popup logic from script.js
            // Set the clicked word in a hidden input or global var if needed
            // Or, you can call the popup logic directly here if refactored
            // For now, trigger the popup as before
            // (You may want to refactor popup logic into a function for reuse)
        }
        // Instead, trigger the popup logic from script.js by dispatching a click event on a hidden span if needed
        // Or, you can refactor popup logic into a global function and call it here
        // For now, just call the popup logic directly if available
        if (window.showPopupForWord) {
            window.showPopupForWord(word, languageSelect ? languageSelect.value : 'en');
        }
    });

    // Initial render
    renderWordCloud();
}); 