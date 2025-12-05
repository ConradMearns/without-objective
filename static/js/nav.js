/**
 * Navigation loader - loads and renders post navigation from manifest.json
 */

let manifestCache = null;

/**
 * Load the manifest.json file
 */
async function loadManifest() {
    if (manifestCache) {
        return manifestCache;
    }

    try {
        const response = await fetch('../manifest.json');
        if (!response.ok) {
            throw new Error(`Failed to load manifest: ${response.status}`);
        }
        manifestCache = await response.json();
        return manifestCache;
    } catch (error) {
        console.error('Error loading manifest:', error);
        return null;
    }
}

/**
 * Format a date string to a readable format
 */
function formatDate(isoDate) {
    const date = new Date(isoDate);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Load and render navigation for post pages
 * @param {string} currentSlug - The slug of the current post to mark as active
 */
async function loadNav(currentSlug) {
    const manifest = await loadManifest();
    if (!manifest || !manifest.posts) {
        console.error('Failed to load manifest or no posts found');
        return;
    }

    const navContainer = document.getElementById('nav-posts');
    if (!navContainer) {
        console.error('Nav container #nav-posts not found');
        return;
    }

    // Generate nav items
    const navItems = manifest.posts.map(post => {
        const isActive = post.slug === currentSlug;
        const activeClass = isActive ? ' class="active"' : '';
        const postFilename = post.html.split('/').pop(); // Get just the filename
        const pdfLink = post.pdf
            ? `<a href="${post.pdf.split('/').pop()}" class="pdf-link" title="Download PDF">📄</a>`
            : '';

        return `
            <div class="post-item"${activeClass}>
                <a href="${postFilename}">${post.title}</a>
                ${pdfLink}
                <div class="post-meta">${formatDate(post.modified)}</div>
            </div>`;
    }).join('');

    navContainer.innerHTML = navItems;
}

/**
 * Load and render posts for the index page
 */
async function loadIndexPosts() {
    const manifest = await loadManifest();
    if (!manifest || !manifest.posts) {
        console.error('Failed to load manifest or no posts found');
        return;
    }

    const postsGrid = document.getElementById('posts-grid');
    if (!postsGrid) {
        console.error('Posts grid #posts-grid not found');
        return;
    }

    // Generate post items
    const postItems = manifest.posts.map(post => {
        const pdfLink = post.pdf
            ? `<a href="${post.pdf}" class="pdf-link" title="Download PDF">📄</a>`
            : '';

        return `
            <div class="post-item">
                <a href="${post.html}">${post.title}</a>
                ${pdfLink}
                <div class="post-meta">${formatDate(post.modified)}</div>
            </div>`;
    }).join('');

    postsGrid.innerHTML = postItems;
}
