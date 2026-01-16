const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Iowa Cooperatives Data
const cooperatives = [
    { id: 1, name: "21st Century Cooperative", website: "http://www.21stcoop.com/" },
    { id: 2, name: "AgState", website: "https://agstate.org/" },
    { id: 3, name: "Archer Cooperative Grain", website: "http://archercoopgrain.com/" },
    { id: 4, name: "Aspinwall Coop Company", website: "http://www.aspinwallcoop.com/" },
    { id: 5, name: "Buckingham Cooperative", website: "http://www.buckingham.coop/" },
    { id: 6, name: "Cedar County Cooperative", website: "http://www.cedarcountycoop.com/" },
    { id: 7, name: "Cooperative Farmers Elevator", website: "http://www.coopfe.com/" },
    { id: 8, name: "Dunkerton Co-op Elevator", website: "http://www.dunkertoncoop.com/" },
    { id: 9, name: "Farm Service Cooperative", website: "http://www.fscoop.com/" },
    { id: 10, name: "Farmers Cooperative", website: "http://www.keotafarmerscoop.com/" },
    { id: 11, name: "Farmers Co-op (Readlyn)", website: "http://www.readlynshellrockcoop.com/" },
    { id: 12, name: "Farmers Cooperative (Radcliffe)", website: "https://www.radcliffecoop.com/" },
    { id: 13, name: "Farmers Cooperative (Craig)", website: "http://craigcoop.com/" },
    { id: 14, name: "Farmers Cooperative (Remsen)", website: "http://www.remsencoop.com/" },
    { id: 15, name: "Farmers Cooperative (Ottosen)", website: "http://www.ottosenelevator.com/" },
    { id: 16, name: "Farmers Cooperative (Arcadia)", website: "http://www.faccooperative.com/" },
    { id: 17, name: "Farmers Cooperative Society", website: "http://www.farmerscoopsociety.com/" },
    { id: 18, name: "Farmers Union Cooperative", website: "http://www.farmerunion.net/" },
    { id: 19, name: "Farmers Win Cooperative", website: "http://www.farmerswin.com/" },
    { id: 20, name: "Five Star Cooperative", website: "https://www.fivestarcoop.com/" },
    { id: 21, name: "Gold-Eagle Cooperative", website: "http://www.goldeaglecoop.com/" },
    { id: 22, name: "Heartland Co-op", website: "http://www.heartlandcoop.com/" },
    { id: 23, name: "Hull Cooperative", website: "http://www.hullcoop.com/" },
    { id: 24, name: "Innovative Ag Services", website: "http://www.innovativeag.com/" },
    { id: 25, name: "Key Cooperative", website: "http://www.keycoop.com/" },
    { id: 26, name: "Landus", website: "https://www.landus.ag/" },
    { id: 27, name: "Linn Cooperative Oil Co.", website: "https://www.linncoop.com/" },
    { id: 28, name: "Mid-Iowa Cooperative", website: "http://www.midiowacoop.com/" },
    { id: 29, name: "NEW Cooperative Inc.", website: "http://www.newcoop.com/" },
    { id: 30, name: "Nexus Cooperative", website: "https://www.nexus.coop/" },
    { id: 31, name: "North Iowa Cooperative", website: "http://www.nicoop.com/" },
    { id: 32, name: "PRO Cooperative", website: "http://www.procooperative.com/" },
    { id: 33, name: "Producer Cooperative", website: "https://gazaproducerscoop.com/" },
    { id: 34, name: "River Valley Cooperative", website: "http://www.rivervalleycoop.com/" },
    { id: 35, name: "SilverEdge Cooperative", website: "http://www.silveredgecoop.com/" },
    { id: 36, name: "Stateline Cooperative", website: "http://www.statelinecoop.com/" },
    { id: 37, name: "Tama-Benton Cooperative", website: "http://www.tamabentoncoop.com/" },
    { id: 38, name: "Two Rivers Cooperative", website: "http://www.tworivers.coop/" },
    { id: 39, name: "United Cooperative", website: "http://www.unitedcoop.com/" },
    { id: 40, name: "Access Energy Cooperative", website: "http://www.accessenergycoop.com/" },
    { id: 41, name: "Allamakee-Clayton REC", website: "http://www.acrec.com/" },
    { id: 42, name: "Butler County REC", website: "http://www.butlerrec.coop/" },
    { id: 43, name: "Calhoun County Electric", website: "https://www.calhounrec.coop/" },
    { id: 44, name: "Central Iowa Power Coop", website: "http://www.cipco.net/" },
    { id: 45, name: "Chariton Valley Electric", website: "https://www.cvrec.com/" },
    { id: 46, name: "Consumers Energy Coop", website: "https://www.consumersenergy.coop/" },
    { id: 47, name: "Corn Belt Power Coop", website: "http://www.cbpower.coop/" },
    { id: 48, name: "Corridor Energy Coop", website: "https://corridorenergy.coop/" },
    { id: 49, name: "East Central Iowa REC", website: "http://www.ecirec.coop/" },
    { id: 50, name: "Farmers Electric Co-op", website: "http://www.farmersrec.com/" },
    { id: 51, name: "Franklin Rural Electric", website: "https://www.franklinrec.coop/" },
    { id: 52, name: "Grundy County REC", website: "http://www.grundycountyrecia.com/" },
    { id: 53, name: "Guthrie County REC", website: "http://www.guthrie-rec.coop/" },
    { id: 54, name: "Harrison County REC", website: "http://www.hcrec.coop/" },
    { id: 55, name: "Iowa Lakes Electric", website: "http://www.ilec.org/" },
    { id: 56, name: "Midland Power Coop", website: "http://www.midlandpower.com/" },
    { id: 57, name: "Nishnabotna Valley REC", website: "https://www.nvrec.com/" },
    { id: 58, name: "Northwest REC", website: "http://www.nwrec.com/" },
    { id: 59, name: "Northwest Iowa Power", website: "http://www.nipco.coop/" },
    { id: 60, name: "Raccoon Valley Electric", website: "http://www.rvec.coop/" },
    { id: 61, name: "Cedar Falls Credit Union", website: "http://www.cfccu.org/" },
    { id: 62, name: "Community Choice CU", website: "http://www.comchoicecu.org/" },
    { id: 63, name: "Community 1st CU", website: "https://www.c1stcreditunion.com/" },
    { id: 64, name: "Dupaco Community CU", website: "https://www.dupaco.com/" },
    { id: 65, name: "Financial Plus CU", website: "https://secure.financialpluscu.com/" },
    { id: 66, name: "Greater Iowa CU", website: "https://www.greateriowacu.org/" },
    { id: 67, name: "Green State CU", website: "https://www.greenstate.org/" },
    { id: 68, name: "Farmers Co-op Telephone", website: "http://www.fctc.coop/" },
    { id: 69, name: "Farmers Mutual Telephone", website: "http://www.fmctc.com/" },
    { id: 70, name: "Heart of Iowa Comm.", website: "http://www.heartofiowa.coop/" },
    { id: 71, name: "Huxley Communications", website: "http://www.huxcomm.net/" },
    { id: 72, name: "Northwest Communications", website: "https://ncn.net/" },
    { id: 73, name: "South Slope Cooperative", website: "https://www.southslope.com/" },
    { id: 74, name: "Western Iowa Telephone", website: "https://www.wiatel.com/" },
    { id: 75, name: "Iowa Food Cooperative", website: "https://iowafood.coop/" },
    { id: 76, name: "Oneota Food Cooperative", website: "https://oneotacoop.com/" },
    { id: 77, name: "New Pioneer Food Co-op", website: "https://www.newpi.coop/" },
    { id: 78, name: "Frontier Co-op", website: "https://www.frontiercoop.com/" },
    { id: 79, name: "Morning Bell Coffee", website: "https://morningbellcoffee.com/" },
    { id: 80, name: "River City Housing", website: "https://rchc.coop/" },
    { id: 81, name: "Prairie Hill Co-Housing", website: "https://www.prairiehillcohousing.org/" },
    { id: 82, name: "Vintage Cooperative", website: "https://www.ewingdevelopment.com/cooperatives" },
    { id: 83, name: "Brown Deer Cooperative", website: "https://www.browndeercooperative.com" },
    { id: 84, name: "Cooperative Energy Co.", website: "http://www.coopenergyco.com/" },
    { id: 85, name: "Hancock County Co-op Oil", website: "https://www.hancockcountycoop.com/" },
    { id: 86, name: "NuWay K&H Cooperative", website: "https://www.nuway-kandh.com/" },
    { id: 87, name: "W & H Oil Cooperative", website: "http://www.whcoop.com/" },
    { id: 88, name: "Siouxland Energy Coop", website: "http://www.siouxlandenergy.com/" }
];

// Create screenshots directory
const screenshotsDir = path.join(__dirname, 'screenshots');
if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
}

async function captureScreenshot(browser, coop) {
    const page = await browser.newPage();
    const filename = `${String(coop.id).padStart(3, '0')}.png`;
    const filepath = path.join(screenshotsDir, filename);
    
    try {
        // Set viewport
        await page.setViewport({ width: 1280, height: 800 });
        
        // Set a reasonable user agent
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
        
        console.log(`[${coop.id}/88] Capturing: ${coop.name}`);
        console.log(`         URL: ${coop.website}`);
        
        // Navigate with timeout
        await page.goto(coop.website, { 
            waitUntil: 'networkidle2',
            timeout: 30000 
        });
        
        // Wait a bit for any animations/lazy content
        await new Promise(r => setTimeout(r, 1500));
        
        // Take screenshot
        await page.screenshot({ 
            path: filepath,
            type: 'png'
        });
        
        console.log(`         ✓ Saved: ${filename}`);
        await page.close();
        return { success: true, id: coop.id, name: coop.name };
        
    } catch (error) {
        console.log(`         ✗ Error: ${error.message}`);
        await page.close();
        return { success: false, id: coop.id, name: coop.name, error: error.message };
    }
}

async function main() {
    console.log('');
    console.log('═'.repeat(60));
    console.log('  Iowa Cooperative Website Screenshot Capture');
    console.log('═'.repeat(60));
    console.log(`  Total cooperatives: ${cooperatives.length}`);
    console.log(`  Output folder: ${screenshotsDir}`);
    console.log('═'.repeat(60));
    console.log('');
    
    // Launch browser
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const results = { successful: [], failed: [] };
    
    // Process each cooperative
    for (const coop of cooperatives) {
        const result = await captureScreenshot(browser, coop);
        if (result.success) {
            results.successful.push(result);
        } else {
            results.failed.push(result);
        }
    }
    
    await browser.close();
    
    // Summary
    console.log('');
    console.log('═'.repeat(60));
    console.log('  SUMMARY');
    console.log('═'.repeat(60));
    console.log(`  ✓ Successful: ${results.successful.length}`);
    console.log(`  ✗ Failed: ${results.failed.length}`);
    
    if (results.failed.length > 0) {
        console.log('');
        console.log('  Failed sites:');
        results.failed.forEach(f => {
            console.log(`    - ${f.id}: ${f.name}`);
        });
    }
    
    console.log('');
    console.log(`  Screenshots saved to: ${screenshotsDir}`);
    console.log('═'.repeat(60));
    console.log('');
}

main().catch(console.error);
