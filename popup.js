
//******************************************************************************************

document.addEventListener('DOMContentLoaded', function() {
    // Load saved settings
    chrome.storage.local.get([
        'colorBlindMode', 'contrast', 'hue',
        'darkMode', 'blueLight', 'nightLight', 'readingMode'
    ], function(result) {
        document.getElementById('contrast').value = result.contrast || 1.3;
        document.getElementById('hue').value = result.hue || 20;
        document.getElementById('darkMode').checked = result.darkMode || false;
        document.getElementById('blueLight').checked = result.blueLight || false;
        document.getElementById('nightLight').checked = result.nightLight || false;
        document.getElementById('readingMode').checked = result.readingMode || false;
        
        // Set initial toggle button state
        document.getElementById('toggleMode').textContent = 
            result.colorBlindMode ? 'Disable' : 'Enable';
    });
});

document.getElementById("toggleMode").addEventListener("click", toggleMode);

document.querySelectorAll(".resetBtn").forEach(btn => {
    btn.addEventListener("click", function() {
        const type = this.dataset.reset;
        if (type === "contrast") {
            document.getElementById('contrast').value = 1.3;
        } else if (type === "hue") {
            document.getElementById('hue').value = 20;
        }
        applyChanges();
    });
});

document.getElementById("contrast").addEventListener("input", applyChanges);
document.getElementById("hue").addEventListener("input", applyChanges);
document.getElementById("darkMode").addEventListener("change", applyChanges);
document.getElementById("blueLight").addEventListener("change", applyChanges);
document.getElementById("nightLight").addEventListener("change", applyChanges);
document.getElementById("readingMode").addEventListener("change", applyChanges);

function toggleMode() {
    chrome.storage.local.get(['colorBlindMode'], (result) => {
        const newMode = !result.colorBlindMode;
        chrome.storage.local.set({ colorBlindMode: newMode }, () => {
            if (newMode) {
                applyChanges();
            } else {
                resetChanges();
            }
            document.getElementById('toggleMode').textContent = newMode ? 'Disable' : 'Enable';
        });
    });
}

function applyChanges() {
    const settings = {
        contrast: document.getElementById('contrast').value,
        hue: document.getElementById('hue').value,
        darkMode: document.getElementById('darkMode').checked,
        blueLight: document.getElementById('blueLight').checked,
        nightLight: document.getElementById('nightLight').checked,
        readingMode: document.getElementById('readingMode').checked
    };

    chrome.storage.local.set({ ...settings, colorBlindMode: true }, () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.scripting.executeScript({
                target: { tabId: tabs[0].id },
                function: applyFilters,
                args: [settings]
            });
        });
    });
}

function resetChanges() {
    chrome.storage.local.set({
        colorBlindMode: false,
        darkMode: false,
        blueLight: false,
        nightLight: false,
        readingMode: false
    }, () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.scripting.executeScript({
                target: { tabId: tabs[0].id },
                function: restoreOriginal
            });
        });
        // Reset UI checkboxes
        document.getElementById('darkMode').checked = false;
        document.getElementById('blueLight').checked = false;
        document.getElementById('nightLight').checked = false;
        document.getElementById('readingMode').checked = false;
    });
}


function applyFilters(settings) {
    let filter = `contrast(${settings.contrast}) hue-rotate(${settings.hue}deg)`;
    
    if (settings.darkMode) filter += ' invert(100%) hue-rotate(180deg)';
    if (settings.blueLight) filter += ' sepia(60%)';
    if (settings.nightLight) filter += ' brightness(80%) sepia(30%)';
    if (settings.readingMode) filter += ' grayscale(100%) contrast(150%)';
    
    document.body.style.filter = filter;
    
    // Original image processing
    document.querySelectorAll("img").forEach(async (img) => {
        if (img.dataset.originalSrc) return;
        img.dataset.originalSrc = img.src;
        try {
            const processed = await processImage(img.src);
            img.src = processed;
        } catch (e) {
            console.error("Image processing failed:", e);
        }
    });
}


async function processImage(src) {
    const response = await fetch("http://127.0.0.1:5000/process_image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_url: src })
    });
    const data = await response.json();
    return data.processed_image;
}

function restoreOriginal() {
    document.body.style.filter = 'none';
    document.querySelectorAll("img").forEach(img => {
        img.style.filter = 'none';
        if (img.dataset.originalSrc) {
            img.src = img.dataset.originalSrc;
            delete img.dataset.originalSrc;
        }
    });
}
