source "https://rubygems.org"

# Using Jekyll 4.x with GitHub Actions (not native GitHub Pages)
# This gives us more flexibility and latest features
gem "jekyll", "~> 4.3.2"

# For native GitHub Pages compatibility (Jekyll 3.9.x), uncomment:
# gem "github-pages", group: :jekyll_plugins

# No plugins needed for this site
group :jekyll_plugins do
  # Add Jekyll plugins here if needed
end

# Windows and JRuby does not include zoneinfo files, so bundle the tzinfo-data gem
# and associated library.
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1", :platforms => [:mingw, :x64_mingw, :mswin]

# Lock `http_parser.rb` gem to `v0.6.x` on JRuby builds since newer versions of the gem
# do not have a Java counterpart.
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]


gem "csv"
gem "logger"
gem "base64"