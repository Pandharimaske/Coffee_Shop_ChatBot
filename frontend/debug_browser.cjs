const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
    page.on('pageerror', error => console.error('BROWSER ERROR:', error));

    console.log("Navigating to http://localhost:5173/");
    try {
        await page.goto('http://localhost:5173/', { waitUntil: 'networkidle', timeout: 5000 });
        console.log("Navigation finished.");
    } catch (e) {
        console.error("Navigation error:", e);
    }
    
    await browser.close();
})();
