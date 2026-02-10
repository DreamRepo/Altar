// Ensure global namespace
window.dash_clientside = Object.assign({}, window.dash_clientside, {
  pyg: {
    open: function(url) {
      if (!url) {
        return window.dash_clientside.no_update;
      }
      try {
        // Try to open in new tab
        var newWindow = window.open(url, "_blank");
        // If blocked by popup blocker, navigate in same tab
        if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
          console.log("Popup blocked, navigating in same tab");
          window.location.href = url;
        }
      } catch (e) {
        // Fallback: navigate in same tab
        window.location.href = url;
      }
      return "";
    }
  }
});

