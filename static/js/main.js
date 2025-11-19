document.addEventListener('DOMContentLoaded', () => {
    const newKeywordInput = document.getElementById('new-keyword');
    const addKeywordBtn = document.getElementById('add-keyword-btn');
    const keywordsContainer = document.getElementById('keywords-container');
    const videoGrid = document.getElementById('video-grid');
    const loadingSpinner = document.getElementById('loading-spinner');
    const refreshFeedBtn = document.getElementById('refresh-feed-btn');

    // Initial Load
    loadKeywords();
    loadFeed();

    // Event Listeners
    addKeywordBtn.addEventListener('click', addKeyword);
    newKeywordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addKeyword();
    });
    refreshFeedBtn.addEventListener('click', loadFeed);

    async function loadKeywords() {
        try {
            const response = await fetch('/api/keywords');
            const keywords = await response.json();
            renderKeywords(keywords);
        } catch (error) {
            console.error('Error loading keywords:', error);
        }
    }

    async function addKeyword() {
        const keyword = newKeywordInput.value.trim();
        if (!keyword) return;

        try {
            const response = await fetch('/api/keywords', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keyword })
            });

            if (response.ok) {
                newKeywordInput.value = '';
                loadKeywords();
                loadFeed(); // Refresh feed to include new keyword
            } else {
                const data = await response.json();
                alert(data.error || 'Failed to add keyword');
            }
        } catch (error) {
            console.error('Error adding keyword:', error);
        }
    }

    async function deleteKeyword(keyword) {
        if (!confirm(`Remove "${keyword}" from your saved keywords?`)) return;

        try {
            const response = await fetch(`/api/keywords/${encodeURIComponent(keyword)}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadKeywords();
                loadFeed(); // Refresh feed to remove videos from this keyword
            }
        } catch (error) {
            console.error('Error deleting keyword:', error);
        }
    }

    function renderKeywords(keywords) {
        keywordsContainer.innerHTML = '';
        keywords.forEach(keyword => {
            const chip = document.createElement('div');
            chip.className = 'badge bg-secondary rounded-pill p-2 px-3 d-flex align-items-center gap-2';
            chip.style.cursor = 'pointer';
            chip.innerHTML = `
                <span>${keyword}</span>
                <span class="btn-close btn-close-white" style="font-size: 0.5rem;"></span>
            `;
            chip.querySelector('.btn-close').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteKeyword(keyword);
            });
            keywordsContainer.appendChild(chip);
        });
    }

    async function loadFeed() {
        showLoading(true);
        videoGrid.innerHTML = '';

        try {
            const response = await fetch('/api/feed');
            const data = await response.json();
            
            if (data.videos && data.videos.length > 0) {
                renderVideos(data.videos);
            } else {
                videoGrid.innerHTML = `
                    <div class="col-12 text-center text-muted py-5">
                        <p class="lead">${data.message || 'No videos found. Add some keywords to get started!'}</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading feed:', error);
            videoGrid.innerHTML = '<div class="col-12 text-center text-danger">Error loading feed.</div>';
        } finally {
            showLoading(false);
        }
    }

    function renderVideos(videos) {
        videos.forEach(video => {
            const col = document.createElement('div');
            col.className = 'col';
            col.dataset.uploader = video.uploader; // For easy removal
            col.innerHTML = `
                <div class="card h-100">
                    <div onclick="window.open('${video.url}', '_blank')">
                        <img src="${video.thumbnail || 'https://via.placeholder.com/320x180?text=No+Thumbnail'}" class="card-img-top" alt="${video.title}">
                    </div>
                    <div class="card-body">
                        <h5 class="card-title" title="${video.title}" onclick="window.open('${video.url}', '_blank')">${video.title}</h5>
                        <p class="card-text">
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">${video.uploader || 'Unknown'}</small>
                                <button class="btn btn-sm btn-outline-danger ban-btn" title="Ban this channel" style="padding: 0.1rem 0.4rem; font-size: 0.7rem;">
                                    &#x2715; Ban
                                </button>
                            </div>
                            <small>${video.view_count ? formatViews(video.view_count) + ' views' : ''}</small>
                            <span class="float-end badge bg-secondary">${formatDuration(video.duration)}</span>
                        </p>
                    </div>
                </div>
            `;
            
            // Add event listener for ban button
            const banBtn = col.querySelector('.ban-btn');
            banBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                banChannel(video.uploader);
            });

            videoGrid.appendChild(col);
        });
    }

    async function banChannel(channelName) {
        if (!channelName) return;
        if (!confirm(`Ban channel "${channelName}"? Videos from this channel will no longer appear in your feed.`)) return;

        try {
            const response = await fetch('/api/ban_channel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ channel_name: channelName })
            });

            if (response.ok) {
                // Remove all videos from this uploader immediately
                const videos = document.querySelectorAll(`[data-uploader="${channelName}"]`);
                videos.forEach(v => v.remove());
            } else {
                alert('Failed to ban channel');
            }
        } catch (error) {
            console.error('Error banning channel:', error);
        }
    }

    function showLoading(isLoading) {
        if (isLoading) {
            loadingSpinner.classList.remove('d-none');
        } else {
            loadingSpinner.classList.add('d-none');
        }
    }

    function formatViews(views) {
        if (views >= 1000000) {
            return (views / 1000000).toFixed(1) + 'M';
        } else if (views >= 1000) {
            return (views / 1000).toFixed(1) + 'K';
        }
        return views;
    }

    function formatDuration(seconds) {
        if (!seconds) return '';
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min}:${sec.toString().padStart(2, '0')}`;
    }
});
