chrome.storage.local.get(["colorBlindMode"], (result) => {
    if (result.colorBlindMode) {
        modifyPage(1.3, 20);
    }
});

function modifyPage(contrast, hue) {
    document.body.style.filter = `contrast(${contrast}) hue-rotate(${hue}deg)`;

    document.querySelectorAll("a").forEach((link) => {
        link.style.textDecoration = "underline";
    });

    document.querySelectorAll("button").forEach((button) => {
        button.style.border = "2px solid black";
    });

    document.querySelectorAll("img").forEach(async (img) => {
        processImage(img);
    });
}

async function processImage(img) {
    let src = img.src;
    let response = await fetch("http://127.0.0.1:5000/process_image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_url: src })
    });

    let data = await response.json();
    if (data.processed_image) img.src = data.processed_image;
}

chrome.storage.local.get([
    'colorBlindMode', 'contrast', 'hue',
    'darkMode', 'blueLight', 'nightLight', 'readingMode'
], (result) => {
    if (result.colorBlindMode) {
        applyFilters(result);
    }
});

async function applyFilters(settings) {
    let filter = `contrast(${settings.contrast || 1.3}) hue-rotate(${settings.hue || 20}deg)`;
    
    if (settings.darkMode) filter += ' invert(100%) hue-rotate(180deg)';
    if (settings.blueLight) filter += ' sepia(60%)';
    if (settings.nightLight) filter += ' brightness(80%) sepia(30%)';
    if (settings.readingMode) filter += ' grayscale(100%) contrast(150%)';
    
    document.body.style.filter = filter;

    document.querySelectorAll("img").forEach(async (img) => {
        processImage(img);
    });
}

// Keep original processImage function unchanged