// Theme toggle with persistence
(function () {
  const root = document.documentElement;
  const preferred = localStorage.getItem("theme");
  if (preferred) root.setAttribute("data-theme", preferred);

  const btn = document.getElementById("themeToggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const current = root.getAttribute("data-theme");
      const next = current === "light" ? "dark" : "light";
      if (!current) {
        // If not set, infer from system; then toggle
        const systemDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        root.setAttribute("data-theme", systemDark ? "light" : "light"); // force set to ensure next works
      }
      const newTheme = (root.getAttribute("data-theme") || "dark") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
      btn.textContent = newTheme === "light" ? "🌙" : "☀️";
    });
  }

  // Set initial icon
  if (btn) {
    const t = root.getAttribute("data-theme");
    btn.textContent = t === "light" ? "🌙" : "☀️";
  }

  // Year in footer
  const y = document.getElementById("year");
  if (y) y.textContent = String(new Date().getFullYear());
})();

// Resource Finder Logic
(function () {
  // Wait for DOM if not ready, otherwise execute immediately
  function initFinder() {
    let selectedProfile = null;
    let selectedApproach = null;
    let selectedGoal = null;
    let selectedDetail = 'detailed'; // Default to detailed
    let resourceDataObj = null;

    // Load resource data from embedded JSON
    const dataEl = document.getElementById('resourceData');
    if (dataEl) {
      try {
        resourceDataObj = JSON.parse(dataEl.textContent);
      } catch (e) {
        console.error('Failed to parse resource data:', e);
      }
    }

  // Selection items
  const finderItems = document.querySelectorAll('.finder-item');
  const showBtn = document.getElementById('showResourcesBtn');
  const resetBtn = document.getElementById('resetBtn');
  const resultsDiv = document.getElementById('resourceResults');

  // Helper function to show results automatically
  function autoShowResults() {
    if (!selectedGoal || !selectedApproach || !resourceDataObj) return;

    const pathKey = `${selectedGoal}_${selectedApproach}`;
    const resourceIds = resourceDataObj.paths[pathKey];

    if (!resourceIds || resourceIds.length === 0) {
      // Hide results if no path exists
      if (resultsDiv) resultsDiv.style.display = 'none';
      return;
    }

    // Build and show results
    displayResults(resourceIds);
  }

  // Helper function to update available options
  function updateAvailableOptions() {
    if (!resourceDataObj) return;

    // Filter goals based on selected profile
    if (selectedProfile && resourceDataObj.profileGoals) {
      const allowedGoals = resourceDataObj.profileGoals[selectedProfile];
      
      document.querySelectorAll('.finder-item[data-type="goal"]').forEach(goalItem => {
        const goalId = goalItem.dataset.id;
        
        if (allowedGoals && allowedGoals.includes(goalId)) {
          goalItem.classList.remove('disabled');
        } else {
          goalItem.classList.add('disabled');
          if (goalItem.classList.contains('selected')) {
            goalItem.classList.remove('selected');
            selectedGoal = null;
          }
        }
      });
    } else {
      // No profile selected, enable all goals
      document.querySelectorAll('.finder-item[data-type="goal"]').forEach(i => 
        i.classList.remove('disabled'));
    }
  }

  finderItems.forEach(item => {
    item.addEventListener('click', () => {
      // Don't allow clicking disabled items
      if (item.classList.contains('disabled')) return;

      const type = item.dataset.type;
      const id = item.dataset.id;

      if (type === 'profile') {
        // Deselect other profiles
        document.querySelectorAll('.finder-item[data-type="profile"]').forEach(i => 
          i.classList.remove('selected'));
        selectedProfile = id;
      } else if (type === 'approach') {
        // Deselect other approaches
        document.querySelectorAll('.finder-item[data-type="approach"]').forEach(i => 
          i.classList.remove('selected'));
        selectedApproach = id;
      } else if (type === 'goal') {
        // Deselect other goals
        document.querySelectorAll('.finder-item[data-type="goal"]').forEach(i => 
          i.classList.remove('selected'));
        selectedGoal = id;
      } else if (type === 'detail') {
        // Deselect other detail levels
        document.querySelectorAll('.finder-item[data-type="detail"]').forEach(i => 
          i.classList.remove('selected'));
        selectedDetail = id;
      }

      item.classList.add('selected');
      
      // Update which options are available
      updateAvailableOptions();
      
      // Auto-show results when all selections are made
      autoShowResults();
    });
  });

  // Reset button
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      selectedProfile = null;
      selectedApproach = null;
      selectedGoal = null;
      finderItems.forEach(item => {
        item.classList.remove('selected');
        item.classList.remove('disabled');
      });
      if (resultsDiv) resultsDiv.style.display = 'none';
      document.getElementById('resource-finder').scrollIntoView({ behavior: 'smooth' });
    });
  }

  function displayResults(resourceIds) {
    if (!resultsDiv || !resourceDataObj) return;

    const timeline = resultsDiv.querySelector('.results-timeline');
    const contextP = resultsDiv.querySelector('.results-context');
    const totalTimeSpan = document.getElementById('totalTime');

    // Clear previous results
    timeline.innerHTML = '';

    // Set context
    const goalLabel = document.querySelector(`.finder-item[data-type="goal"][data-id="${selectedGoal}"] .finder-text`);
    const approachLabel = document.querySelector(`.finder-item[data-type="approach"][data-id="${selectedApproach}"] .finder-text`);
    contextP.textContent = `${goalLabel?.textContent} using ${approachLabel?.textContent}`;

    // Create resource cards
    resourceIds.forEach((id, index) => {
      const res = resourceDataObj.resources[id];
      if (!res) return;

      // Choose description based on detail level
      const descriptionText = selectedDetail === 'quick' ? res.short_description : res.description;

      const card = document.createElement('div');
      card.className = 'resource-card';
      card.innerHTML = `
        <div class="resource-number">${index + 1}</div>
        <div class="resource-content">
          <div class="resource-header">
            <i class="${res.icon}"></i>
            <h4>${res.title}</h4>
          </div>
          <p class="resource-description">${descriptionText}</p>
          <a href="${res.link}" class="btn btn-link" target="${res.link.startsWith('http') ? '_blank' : '_self'}">
            ${res.link_text} <i class="fa-solid fa-arrow-right"></i>
          </a>
        </div>
      `;
      timeline.appendChild(card);
    });

    resultsDiv.style.display = 'block';
  }
  
  } // end initFinder
  
  // Run immediately since script is at bottom of body
  initFinder();
})();

// Simple Site Search (client-side)
(function () {
  const inputs = document.querySelectorAll('.search-input');
  if (!inputs.length) return;

  let indexEntries = [];
  const idxUrl = (window.__searchIndex || 'search.json');
  fetch(idxUrl)
    .then(r => r.json())
    .then(data => {
      indexEntries = data.entries || [];
    })
    .catch(() => {
      // Fallback minimal index
      indexEntries = [
        { title: 'Installation', url: '/', content: '' },
        { title: 'Sender', url: 'sender', content: '' },
        { title: 'Viewer', url: 'viewer', content: '' },
        { title: 'Extractor', url: 'extractor', content: '' },
        { title: 'Deploy', url: 'deploy', content: '' },
        { title: 'Manage Users', url: 'manage', content: '' },
        { title: 'Backup/Transfer', url: 'backup', content: '' },
      ];
    });
  
    // Enter: redirect to search page with query
    inputs.forEach(input => {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const q = input.value.trim();
          if (q.length > 0) {
            const target = window.__searchPage || 'search';
            const base = target.endsWith('.html') ? target : target;
            window.location.href = `${base}?q=${encodeURIComponent(q)}`;
          }
        }
      });
    });

  function attachSearch(input) {
    const results = input.nextElementSibling && input.nextElementSibling.classList.contains('search-results')
      ? input.nextElementSibling : null;
    if (!results) return;

    function render(list) {
      if (!list || list.length === 0) {
        results.style.display = 'none';
        results.innerHTML = '';
        return;
      }
      results.innerHTML = list.map(p => `<a href="${p.url}">${p.title}</a>`).join('');
      results.style.display = 'block';
    }

    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      if (q.length === 0) return render([]);

      const tokens = q.split(/\s+/).filter(Boolean);
      const filtered = indexEntries.filter(p => {
        const hay = `${p.title} ${p.content || ''}`.toLowerCase();
        // Require all tokens to be present (AND search)
        return tokens.every(t => hay.includes(t));
      }).slice(0, 10);

      render(filtered);
    });

    document.addEventListener('click', (e) => {
      if (e.target !== input && !results.contains(e.target)) {
        render([]);
      }
    });
  }

  inputs.forEach(attachSearch);
})();

  // Search Results Page Renderer
  (function () {
    const container = document.getElementById('searchPageResults');
    if (!container) return;

    const params = new URLSearchParams(window.location.search);
    const q = (params.get('q') || '').trim();
    const idxUrl = (window.__searchIndex || 'search.json');

    function highlight(text, tokens) {
      let t = text;
      tokens.forEach(tok => {
        const re = new RegExp(`(${tok.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        t = t.replace(re, '<mark>$1</mark>');
      });
      return t;
    }

    function excerpt(content, tokens, len=180) {
      const lc = content.toLowerCase();
      let pos = -1;
      for (const tok of tokens) {
        pos = lc.indexOf(tok.toLowerCase());
        if (pos !== -1) break;
      }
      if (pos === -1) pos = 0;
      const start = Math.max(0, pos - Math.floor(len/3));
      const end = Math.min(content.length, start + len);
      let snippet = content.slice(start, end);
      if (start > 0) snippet = '…' + snippet;
      if (end < content.length) snippet = snippet + '…';
      return highlight(snippet, tokens);
    }

    function renderResults(entries, tokens) {
      if (!entries.length) {
        container.innerHTML = '<p class="lead">No results found.</p>';
        return;
      }
      container.innerHTML = entries.map(e => {
        const ex = excerpt(e.content || '', tokens);
        const url = e.url || '#';
        return `
          <div class="search-item">
            <h3 class="search-title"><a href="${url}">${e.title}</a></h3>
            <p class="search-excerpt">${ex}</p>
          </div>
        `;
      }).join('');
    }

    fetch(idxUrl)
      .then(r => r.json())
      .then(data => {
        const entries = (data.entries || []);
        const tokens = q.toLowerCase().split(/\s+/).filter(Boolean);
        // Rank by number of token hits (OR search, more matches first)
        const ranked = entries
          .map(e => {
            const hay = `${e.title} ${e.content || ''}`.toLowerCase();
            const hits = tokens.reduce((acc, t) => acc + (hay.includes(t) ? 1 : 0), 0);
            return { e, hits };
          })
          .filter(x => x.hits > 0)
          .sort((a,b) => b.hits - a.hits)
          .map(x => x.e)
          .slice(0, 20);
        renderResults(ranked, tokens);
      })
      .catch(() => {
        container.innerHTML = '<p class="lead">Search is unavailable right now.</p>';
      });
  })();

// Remote README fallback: fetch raw markdown from GitHub if available
(function () {
  const containers = document.querySelectorAll('.readme-remote');
  if (!containers.length) return;

  containers.forEach(async (el) => {
    const repo = el.getAttribute('data-repo');
    const branch = el.getAttribute('data-branch') || 'main';
    let path = el.getAttribute('data-path') || '';
    if (!repo || !path) return;

    // If path contains a leading repo folder (e.g., AltarDocker/DEPLOY.md), strip it
    try {
      const repoName = repo.split('/').pop();
      if (path.startsWith(repoName + '/')) {
        path = path.substring(repoName.length + 1);
      }
    } catch (_) {}

    const rawUrl = `https://raw.githubusercontent.com/${repo}/${branch}/${path}`;
    try {
      const res = await fetch(rawUrl, { cache: 'no-store' });
      if (!res.ok) return; // leave server-rendered content
      const md = await res.text();
      if (typeof window.marked === 'function') {
        el.innerHTML = window.marked.parse(md);
      } else {
        // Minimal safe fallback if marked is unavailable
        const esc = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        el.innerHTML = `<pre>${esc}</pre>`;
      }
      el.style.display = 'block';
    } catch (e) {
      // Fail silently; server-side include likely succeeded
    }
  });
})();
