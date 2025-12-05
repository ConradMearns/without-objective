/**
 * Comments System for TypstBlog
 * Adds email-based commenting to blog posts
 */

let currentPost = '';
let currentCommit = '';
const EMAIL = 'roncad@pm.me'; // Base email address

// Initialize commenting system after a post is loaded
function initComments(postSlug, commitHash) {
    currentPost = postSlug;
    currentCommit = commitHash;

    console.log(`Initializing comments for ${postSlug} (${commitHash})`);

    // Find all paragraphs in the content area
    const paragraphs = document.querySelectorAll('#content p');

    paragraphs.forEach((p, idx) => {
        // Add data attributes for tracking
        p.dataset.blockId = `p${idx}`;
        p.classList.add('commentable');

        // Create comment button (hidden by default)
        const commentBtn = createCommentButton(p, idx);
        p.appendChild(commentBtn);

        // Show comment button on hover
        p.addEventListener('mouseenter', () => {
            commentBtn.classList.add('visible');
        });

        p.addEventListener('mouseleave', () => {
            commentBtn.classList.remove('visible');
        });
    });

    // Also handle headings
    const headings = document.querySelectorAll('#content h1, #content h2, #content h3');
    headings.forEach((h, idx) => {
        h.dataset.blockId = `h${idx}`;
        h.classList.add('commentable');

        const commentBtn = createCommentButton(h, `h${idx}`);
        h.appendChild(commentBtn);

        h.addEventListener('mouseenter', () => {
            commentBtn.classList.add('visible');
        });

        h.addEventListener('mouseleave', () => {
            commentBtn.classList.remove('visible');
        });
    });
}

// Create the comment button element
function createCommentButton(element, blockId) {
    const btn = document.createElement('a');
    btn.className = 'comment-btn';
    btn.innerHTML = '💬';
    btn.title = 'Comment via email';

    // Build the email address with context
    const emailAddress = `${EMAIL.split('@')[0]}+${currentPost}-${currentCommit}-${blockId}@${EMAIL.split('@')[1]}`;

    // Get text preview for email subject/body
    const textPreview = element.textContent.trim().substring(0, 50);
    const subject = encodeURIComponent(`Re: ${currentPost} - ${blockId}`);
    const body = encodeURIComponent(`Regarding: "${textPreview}..."\n\nBlock: ${blockId}\nCommit: ${currentCommit}\n\n---\n\n[Your comment here]`);

    btn.href = `mailto:${emailAddress}?subject=${subject}&body=${body}`;

    // Prevent the mailto from also triggering on the parent element
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    return btn;
}

// Optional: Handle text selection for more precise commenting
function handleTextSelection() {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();

    if (selectedText.length > 0) {
        // Find the parent paragraph
        let node = selection.anchorNode;
        while (node && node.nodeType !== 1) {
            node = node.parentNode;
        }

        if (node && node.dataset.blockId) {
            const blockId = node.dataset.blockId;
            const emailAddress = `${EMAIL.split('@')[0]}+${currentPost}-${currentCommit}-${blockId}@${EMAIL.split('@')[1]}`;
            const subject = encodeURIComponent(`Re: "${selectedText.substring(0, 30)}..."`);
            const body = encodeURIComponent(`You highlighted:\n"${selectedText}"\n\nBlock: ${blockId}\nCommit: ${currentCommit}\n\n---\n\n[Your comment here]`);

            console.log(`Selection mailto: ${emailAddress}?subject=${subject}`);
            // Could show a floating button here for selected text
        }
    }
}

// Optional: Add selection handler
document.addEventListener('mouseup', handleTextSelection);

// Debug helper
window.commentDebug = () => {
    console.log(`Post: ${currentPost}`);
    console.log(`Commit: ${currentCommit}`);
    console.log(`Commentable elements: ${document.querySelectorAll('.commentable').length}`);
};
