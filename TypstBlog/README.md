# TypstBlog

A statically-generated blog with email-based commenting, built with Typst, HTMX, and vanilla JavaScript.

## Features

- 📝 Write posts in [Typst](https://typst.app) with beautiful math and diagrams
- 📄 Automatic PDF generation for each post
- 💬 Email-based commenting (no backend required!)
- 🚀 Fully static - deploy anywhere
- ⚡ HTMX-powered navigation
- 🎨 Clean, responsive design with dark mode support

## Quick Start

### Prerequisites

1. **Typst** - Install from https://typst.app or:
   ```bash
   curl -fsSL https://typst.app/install.sh | sh
   ```

2. **uv** (optional) - For running the build script:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### Build the Blog

1. Write posts in `src/*.typ`
2. Run the build script:
   ```bash
   ./build.py
   ```
3. Serve the `dist/` folder:
   ```bash
   cd dist && python -m http.server 8000
   ```
4. Open http://localhost:8000

## How It Works

### Writing Posts

Create `.typ` files in the `src/` directory:

```typst
#set page(width: 16cm, height: auto, margin: 1.5cm)
#set text(font: "Linux Libertine", size: 11pt)

= My Blog Post Title

Your content here with beautiful math:

$ sum_(i=1)^n i = (n(n+1))/2 $
```

### Build Process

The `build.py` script:
1. Finds all `.typ` files in `src/`
2. Compiles each to HTML and PDF
3. Injects git commit hash for version tracking
4. Generates a `manifest.json` with post metadata

### Comment System

When readers hover over paragraphs or headings, a 💬 button appears. Clicking it opens their email client with:
- **To:** `roncad+<post>-<commit>-<block>@pm.me`
- **Subject:** Context about what they're commenting on
- **Body:** Pre-filled with the text they're referencing

The email address encodes:
- Post slug (identifies which post)
- Git commit hash (which version they read)
- Block ID (which paragraph/heading)

This lets you:
- Filter comments by post using email rules
- Track which version of the post they read
- Know exactly what they're commenting on

### HTMX Shell

The `index.html` is a lightweight shell that:
1. Loads the post manifest
2. Uses HTMX to fetch post HTML on click
3. Injects the comment system after each load
4. Provides PDF download links

## Project Structure

```
TypstBlog/
├── build.py              # Build script
├── src/                  # Typst source files
│   └── *.typ
└── dist/                 # Generated site (serve this)
    ├── index.html        # HTMX shell
    ├── manifest.json     # Post metadata
    ├── posts/
    │   ├── *.html        # Post HTML fragments
    │   └── *.pdf         # PDF downloads
    ├── js/
    │   └── comments.js   # Comment system
    ├── css/
    │   └── style.css     # Styling
    └── comments/         # Future: static comment files
```

## Customization

### Email Address

Edit the `EMAIL` constant in `dist/js/comments.js`:
```javascript
const EMAIL = 'your-email@domain.com';
```

### Styling

Modify `dist/css/style.css`. CSS variables at the top control colors:
```css
:root {
    --bg-color: #ffffff;
    --text-color: #1a1a1a;
    --accent-color: #0066cc;
    /* ... */
}
```

### Typst Settings

Each post can override Typst settings:
```typst
#set page(width: 20cm)  // Wider layout
#set text(size: 12pt)   // Larger text
```

## Future Enhancements

- **Display Comments:** Load curated comments from `dist/comments/*.html`
- **RSS Feed:** Generate from manifest.json
- **Search:** Client-side search across posts
- **Tags/Categories:** Add metadata to manifest
- **GitHub Actions:** Auto-build on push

## Deployment

The `dist/` folder is a static site. Deploy to:
- **GitHub Pages:** Push to `gh-pages` branch
- **Netlify:** Connect repo and set publish dir to `dist/`
- **Any static host:** Upload `dist/` contents

## License

MIT (or your choice)
