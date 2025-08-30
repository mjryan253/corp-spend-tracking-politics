/**
 * Build script for Corporate Spending Tracker Frontend
 * Bundles JavaScript dependencies and optimizes for production
 */

const fs = require('fs');
const path = require('path');

// Configuration
const BUILD_CONFIG = {
    // Source files
    src: {
        dependencies: [
            'node_modules/alpinejs/dist/cdn.min.js',
            'node_modules/chart.js/dist/chart.min.js'
        ],
        app: [
            'config.js',
            'logger.js'
        ]
    },
    
    // Output
    dist: {
        dir: 'dist',
        js: 'app.bundle.js',
        css: 'tailwind.css'
    }
};

// Ensure dist directory exists
function ensureDistDirectory() {
    if (!fs.existsSync(BUILD_CONFIG.dist.dir)) {
        fs.mkdirSync(BUILD_CONFIG.dist.dir, { recursive: true });
        console.log('📁 Created dist directory');
    }
}

// Bundle JavaScript files
function bundleJavaScript() {
    console.log('📦 Bundling JavaScript files...');
    
    let bundledContent = '';
    
    // Add header comment
    bundledContent += `/**
 * Corporate Spending Tracker - Bundled JavaScript
 * Generated: ${new Date().toISOString()}
 * 
 * This file contains:
 * - Alpine.js
 * - Chart.js
 * - Application configuration
 * - Frontend logger
 */

`;

    // Bundle dependencies
    console.log('  - Dependencies:');
    BUILD_CONFIG.src.dependencies.forEach(dep => {
        if (fs.existsSync(dep)) {
            const content = fs.readFileSync(dep, 'utf8');
            bundledContent += `\n/* === ${path.basename(dep)} === */\n`;
            bundledContent += content + '\n';
            console.log(`    ✅ ${dep}`);
        } else {
            console.warn(`    ⚠️  ${dep} not found - run 'npm install' first`);
        }
    });

    // Bundle app files
    console.log('  - Application files:');
    BUILD_CONFIG.src.app.forEach(appFile => {
        if (fs.existsSync(appFile)) {
            const content = fs.readFileSync(appFile, 'utf8');
            bundledContent += `\n/* === ${appFile} === */\n`;
            bundledContent += content + '\n';
            console.log(`    ✅ ${appFile}`);
        } else {
            console.warn(`    ⚠️  ${appFile} not found`);
        }
    });

    // Write bundled file
    const outputPath = path.join(BUILD_CONFIG.dist.dir, BUILD_CONFIG.dist.js);
    fs.writeFileSync(outputPath, bundledContent);
    
    const fileSize = (fs.statSync(outputPath).size / 1024).toFixed(2);
    console.log(`✅ JavaScript bundle created: ${outputPath} (${fileSize} KB)`);
}

// Update HTML to use bundled files
function updateHtmlForProduction() {
    console.log('🔧 Updating HTML for production...');
    
    const htmlPath = 'index.html';
    const prodHtmlPath = 'index.prod.html';
    
    if (!fs.existsSync(htmlPath)) {
        console.error(`❌ ${htmlPath} not found`);
        return;
    }
    
    let htmlContent = fs.readFileSync(htmlPath, 'utf8');
    
    // Replace CDN links with bundled files
    htmlContent = htmlContent
        // Remove individual script tags
        .replace(/<script defer src="https:\/\/unpkg\.com\/alpinejs@3\.x\.x\/dist\/cdn\.min\.js"><\/script>/g, '')
        .replace(/<script src="https:\/\/cdn\.jsdelivr\.net\/npm\/chart\.js"><\/script>/g, '')
        .replace(/<script src="config\.js"><\/script>/g, '')
        .replace(/<script src="logger\.js"><\/script>/g, '')
        
        // Replace Tailwind CDN with local build
        .replace(/<script src="https:\/\/cdn\.tailwindcss\.com"><\/script>/g, 
                '<link rel="stylesheet" href="dist/tailwind.css">')
        
        // Add bundled JS before closing head tag
        .replace(/<\/head>/, '    <script src="dist/app.bundle.js"></script>\n</head>');
    
    fs.writeFileSync(prodHtmlPath, htmlContent);
    console.log(`✅ Production HTML created: ${prodHtmlPath}`);
}

// Generate deployment info
function generateDeploymentInfo() {
    const deploymentInfo = {
        buildTime: new Date().toISOString(),
        version: require('./package.json').version,
        files: {
            html: 'index.prod.html',
            css: `dist/${BUILD_CONFIG.dist.css}`,
            js: `dist/${BUILD_CONFIG.dist.js}`
        },
        dependencies: {
            alpinejs: require('./node_modules/alpinejs/package.json').version,
            chartjs: require('./node_modules/chart.js/package.json').version,
            tailwindcss: require('./node_modules/tailwindcss/package.json').version
        }
    };
    
    fs.writeFileSync(
        path.join(BUILD_CONFIG.dist.dir, 'build-info.json'), 
        JSON.stringify(deploymentInfo, null, 2)
    );
    
    console.log('📋 Build info generated: dist/build-info.json');
}

// Main build function
function build() {
    console.log('🚀 Building Corporate Spending Tracker Frontend...\n');
    
    try {
        ensureDistDirectory();
        bundleJavaScript();
        updateHtmlForProduction();
        generateDeploymentInfo();
        
        console.log('\n✅ Build completed successfully!');
        console.log('\n📁 Generated files:');
        console.log(`   - index.prod.html (production-ready HTML)`);
        console.log(`   - dist/${BUILD_CONFIG.dist.js} (bundled JavaScript)`);
        console.log(`   - dist/${BUILD_CONFIG.dist.css} (compiled CSS - run 'npm run build:css')`);
        console.log(`   - dist/build-info.json (build metadata)`);
        
        console.log('\n🚀 To deploy:');
        console.log('   1. Run "npm run build:css" to compile Tailwind CSS');
        console.log('   2. Upload index.prod.html and dist/ folder to your web server');
        console.log('   3. Configure your web server to serve index.prod.html as the main page');
        
    } catch (error) {
        console.error('❌ Build failed:', error.message);
        process.exit(1);
    }
}

// Check if dependencies are installed
function checkDependencies() {
    const missing = BUILD_CONFIG.src.dependencies.filter(dep => !fs.existsSync(dep));
    if (missing.length > 0) {
        console.error('❌ Missing dependencies. Run "npm install" first.');
        console.error('Missing files:', missing);
        process.exit(1);
    }
}

// Run build if called directly
if (require.main === module) {
    checkDependencies();
    build();
}

module.exports = { build, BUILD_CONFIG };
