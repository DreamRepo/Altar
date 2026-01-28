# Altar Documentation Editing Guide

This repository uses **Jekyll** for GitHub Pages, making it easy to edit and maintain documentation.

## 📁 File Structure

```
Altar/
├── _config.yml           # Jekyll configuration
├── _data/                # Content data in YAML format (EDIT THESE!)
│   ├── index.yml         # Home page content
│   ├── sender.yml        # AltarSender page content
│   ├── docker.yml        # AltarDocker page content
│   └── extractor.yml     # AltarExtractor page content
├── _layouts/             # Page templates (rarely need editing)
│   ├── default.html      # Base layout
│   ├── home.html         # Home page layout
│   └── app.html          # App pages layout
├── assets/               # CSS and JavaScript
│   ├── styles.css        # Site styles
│   └── script.js         # Theme toggle and interactions
├── index.html            # Home page (just front matter)
├── sender.html           # AltarSender page (just front matter)
├── docker.html           # AltarDocker page (just front matter)
└── extractor.html        # AltarExtractor page (just front matter)
```

## ✏️ How to Edit Content

### Editing Page Content

All page content is stored in **YAML files** in the `_data/` folder. This makes editing easy without touching HTML:

#### **Home Page** (`_data/index.yml`)

```yaml
meta:
  title: "Altar — Sacred experiment database tools"
  description: "Your description here"

hero:
  title: "Altar"
  subtitle: "Your subtitle with <strong>HTML</strong> support"
  primary_cta:
    text: "Get started"
    link: "#tools"
  secondary_cta:
    text: "View on GitHub"
    link: "https://github.com/DreamRepo"

tools:
  - icon: "fa-solid fa-cubes"
    title: "Tool Name"
    description: "Tool description"
    link: "page.html"
    linkText: "Learn more →"

features:
  - icon: "fa-solid fa-database"
    title: "Feature Name"
    description: "Feature description"

workflow:
  title: "How it works"
  steps:
    - title: "Step 1"
      description: "Step description"
```

#### **App Pages** (`_data/sender.yml`, `docker.yml`, `extractor.yml`)

```yaml
meta:
  title: "Page Title"
  description: "Page description"

hero:
  icon: "fa-solid fa-icon-name"
  title: "App Name"
  subtitle: "App subtitle with <strong>HTML</strong>"
  primary_cta:
    text: "Button Text"
    link: "#features"
  secondary_cta:
    text: "View source"
    link: "https://github.com/..."

features:
  - icon: "fa-solid fa-icon"
    title: "Feature Name"
    description: "Feature description"

quick_start:
  - title: "Step Title"
    code: |
      # Multi-line code block
      command here
    content: "Additional text (optional)"

# Optional sections:
file_categories:      # For sender.yml
  - label: "Label"
    value: "Description"

default_urls:         # For docker.yml
  - label: "Service"
    value: "<code>URL</code>"

environment_vars:     # For extractor.yml
  - label: "VAR_NAME"
    value: "Description"

viewing_results:      # For sender.yml
  - label: "Type"
    value: "Location"

related_tools:
  - icon: "fa-solid fa-icon"
    title: "Tool Name"
    description: "Description"
    link: "page.html"
```

### Editing Styles

Edit [`assets/styles.css`](assets/styles.css) to change colors, fonts, spacing, etc.

### Editing Page Structure

Only edit layout files in `_layouts/` if you need to change the structure:
- [`_layouts/default.html`](_layouts/default.html) - Base HTML template
- [`_layouts/home.html`](_layouts/home.html) - Home page structure
- [`_layouts/app.html`](_layouts/app.html) - App pages structure

## 🚀 Testing Locally

### Prerequisites
```bash
# Install Ruby (required for Jekyll)
# On Windows: https://rubyinstaller.org/
# On macOS: brew install ruby
# On Linux: sudo apt-get install ruby-full

# Install Jekyll and Bundler
gem install jekyll bundler
```

### Running Locally

```bash
# Navigate to the Altar directory
cd Altar

# Install dependencies (first time only)
bundle install

# Serve the site locally
bundle exec jekyll serve

# Open http://localhost:4000/Altar/ in your browser
```

### Using Docker (Alternative)

```bash
# Run Jekyll in Docker
docker run --rm -v ${PWD}:/srv/jekyll -p 4000:4000 jekyll/jekyll:4.2.2 jekyll serve --watch --force_polling
```

## 📝 Common Editing Tasks

### Adding a New Feature

Edit the appropriate `_data/*.yml` file:

```yaml
features:
  - icon: "fa-solid fa-star"  # Font Awesome icon
    title: "New Feature"
    description: "What this feature does"
```

### Changing Button Links

```yaml
hero:
  primary_cta:
    text: "New Text"
    link: "#new-section"  # Use #anchor or full URL
```

### Adding Code Examples

```yaml
quick_start:
  - title: "Installation"
    code: |
      pip install package
      python app.py
    content: "Additional explanation"
```

### Updating Icons

Use [Font Awesome 6](https://fontawesome.com/icons) icons:

```yaml
icon: "fa-solid fa-icon-name"
```

## 🌐 GitHub Pages Deployment

GitHub Pages automatically builds and deploys when you push to the `main` branch.

- **Site URL**: `https://dreamrepo.github.io/Altar/`
- **Build time**: Usually 1-3 minutes after push
- **View build status**: Repository → Actions tab

### Submodules and Embedded READMEs

Some app pages (e.g., AltarSender, AltarExtractor, AltarViewer) embed the README from their submodules using a Jekyll include. This keeps the docs in sync with each tool’s own repository.

- The page front matter sets:
  - `readme_path: "AltarSender/README.md"` (or the appropriate submodule path)
  - The layout includes `submodule_readme.html`, which renders that file in-place
- Submodules are excluded from direct publishing, but `include_relative` reads their README contents for rendering

To work with submodules:

1. Clone with submodules:
  ```bash
  git clone https://github.com/DreamRepo/Altar.git --recurse-submodules
  ```
2. If already cloned, initialize and update:
  ```bash
  git submodule update --init --recursive
  ```
3. To pull latest submodule content (e.g., to refresh embedded READMEs):
  ```bash
  git submodule update --remote --recursive
  git commit -am "chore: update submodules"
  git push
  ```

CI note (GitHub Actions): ensure the checkout step fetches submodules so the README includes render correctly:

```yaml
- uses: actions/checkout@v4
  with:
   submodules: true
```

### Deployment Configuration

In [`_config.yml`](_config.yml):

```yaml
url: "https://dreamrepo.github.io"  # Your GitHub Pages domain
baseurl: "/Altar"                    # Repository name
```

## 🎨 Icons Reference

This site uses [Font Awesome 6](https://fontawesome.com/search). Popular icons:

```yaml
fa-solid fa-database      # Database
fa-solid fa-cloud         # Cloud
fa-solid fa-cubes         # Stack/Docker
fa-solid fa-paper-plane   # Send
fa-solid fa-chart-line    # Metrics
fa-solid fa-filter        # Filter
fa-solid fa-file-csv      # CSV
fa-solid fa-magnifying-glass-chart  # Search/Analysis
```

## 🐛 Troubleshooting

### Site not updating after push?
- Check GitHub Actions for build errors
- Clear browser cache (Ctrl+Shift+R)
- Wait 1-3 minutes for deployment

### YAML syntax error?
- Check indentation (use spaces, not tabs)
- Validate YAML: https://www.yamllint.com/
- Look for missing colons or quotes

### Content not showing?
- Verify the `data_file` matches the YAML filename
- Check front matter in HTML files
- Ensure YAML structure matches the layout

## 📚 Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Guide](https://docs.github.com/en/pages)
- [YAML Syntax](https://yaml.org/spec/1.2.2/)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [Markdown Guide](https://www.markdownguide.org/)

## 💡 Tips

1. **Always test locally** before pushing
2. **Use HTML in YAML** for formatting: `<strong>`, `<code>`, `<br>`
3. **Keep YAML files tidy** - proper indentation is crucial
4. **Font Awesome icons** are free to use
5. **Commit small changes** to track what works

---

**Happy editing! 🎉**

For questions or issues, see the [main README](README.md) or open an issue on GitHub.
