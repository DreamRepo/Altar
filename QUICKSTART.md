# Quick Start for Local Jekyll Development

## Windows Setup (PowerShell)

### 1. Install Ruby

Download and install Ruby+Devkit from [RubyInstaller](https://rubyinstaller.org/downloads/):
- Get the latest **Ruby+Devkit 3.2.x (x64)** version
- Run the installer and select "Add Ruby executables to PATH"
- At the end, run `ridk install` and select option 3 (MSYS2 and MINGW development toolchain)

### 2. Install Jekyll

```powershell
# Open PowerShell
gem install jekyll bundler
```

### 3. Install Project Dependencies

```powershell
cd C:\Users\Alienor\Documents\Projects\DREAM\DATABASE\Altar
bundle install
```

### 4. Serve the Site

```powershell
bundle exec jekyll serve --watch --livereload
```

Open [http://localhost:4000/Altar/](http://localhost:4000/Altar/) in your browser.

The `--watch` flag automatically rebuilds when you edit files.
The `--livereload` flag auto-refreshes your browser.

## Editing Workflow

1. **Edit content** in `_data/*.yml` files
2. **Save the file**
3. **Jekyll rebuilds automatically** (watch for console messages)
4. **Browser refreshes** (with livereload)

## Common Commands

```powershell
# Serve with live reload
bundle exec jekyll serve --watch --livereload

# Serve on custom port
bundle exec jekyll serve --port 4001

# Build without serving
bundle exec jekyll build

# Clean build artifacts
bundle exec jekyll clean

# Update dependencies
bundle update
```

## Troubleshooting

### Port already in use?
```powershell
# Kill process on port 4000
netstat -ano | findstr :4000
taskkill /PID <PID_NUMBER> /F
```

### Build errors?
```powershell
# Clean and rebuild
bundle exec jekyll clean
bundle exec jekyll serve
```

### Update Jekyll?
```powershell
bundle update jekyll
```

## File Editing Tips

- **Content**: Edit `_data/*.yml` files
- **Styles**: Edit `assets/styles.css`
- **Structure**: Only touch `_layouts/*.html` if needed
- **Test locally** before pushing to GitHub!

## GitHub Pages

Once you push to GitHub, the site deploys automatically at:
https://dreamrepo.github.io/Altar/

Build time: 1-3 minutes after push.
