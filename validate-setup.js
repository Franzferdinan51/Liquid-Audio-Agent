/**
 * Setup Validation Script for Liquid Audio Agent + N8N
 *
 * This script validates that everything is properly configured
 * for the CORS fix to work correctly.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Liquid Audio Agent + N8N Setup Validation');
console.log('');

// Check if required files exist
function checkFiles() {
    console.log('📁 Checking required files...');

    const requiredFiles = [
        'fix-cors.bat',
        'fix-cors.sh',
        'fix-cors.ps1',
        'CORS-SOLUTION.md',
        'services/n8nService.ts',
        'test-cors-connection.js'
    ];

    let allFilesExist = true;

    requiredFiles.forEach(file => {
        const filePath = path.join(__dirname, file);
        const exists = fs.existsSync(filePath);
        console.log(`   ${exists ? '✅' : '❌'} ${file}`);
        if (!exists) {
            allFilesExist = false;
        }
    });

    return allFilesExist;
}

// Check Node.js and npm
function checkNodeAndNpm() {
    console.log('📦 Checking Node.js and npm...');

    try {
        const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
        const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();

        console.log(`   ✅ Node.js: ${nodeVersion}`);
        console.log(`   ✅ npm: ${npmVersion}`);
        return true;
    } catch (error) {
        console.log('   ❌ Node.js or npm not found');
        console.log('   💡 Please install Node.js from https://nodejs.org/');
        return false;
    }
}

// Check if n8n is available
function checkN8N() {
    console.log('🤖 Checking n8n installation...');

    try {
        const n8nVersion = execSync('npx n8n --version', { encoding: 'utf8' }).trim();
        console.log(`   ✅ n8n: ${n8nVersion}`);
        return true;
    } catch (error) {
        console.log('   ❌ n8n not found');
        console.log('   💡 Install n8n with: npm install -g n8n');
        return false;
    }
}

// Check if React app dependencies are installed
function checkReactDependencies() {
    console.log('⚛️  Checking React app dependencies...');

    const packageJsonPath = path.join(__dirname, 'package.json');
    const nodeModulesPath = path.join(__dirname, 'node_modules');

    if (!fs.existsSync(packageJsonPath)) {
        console.log('   ❌ package.json not found');
        return false;
    }

    if (!fs.existsSync(nodeModulesPath)) {
        console.log('   ❌ node_modules not found');
        console.log('   💡 Run: npm install');
        return false;
    }

    console.log('   ✅ Dependencies installed');
    return true;
}

// Check current running processes
function checkRunningProcesses() {
    console.log('🔄 Checking for running processes...');

    try {
        // This is a simple check - in a real implementation you'd want more sophisticated process checking
        if (process.platform === 'win32') {
            try {
                execSync('tasklist | findstr node.exe', { stdio: 'ignore' });
                console.log('   ⚠️  Node.js processes are running');
                console.log('   💡 You may need to stop them before running the CORS fix');
            } catch {
                console.log('   ✅ No conflicting Node.js processes found');
            }
        } else {
            try {
                execSync('pgrep -f "node.*n8n"', { stdio: 'ignore' });
                console.log('   ⚠️  N8N processes are running');
                console.log('   💡 The fix script will stop them automatically');
            } catch {
                console.log('   ✅ No N8N processes found');
            }
        }
    } catch (error) {
        console.log('   ⚠️  Could not check running processes');
    }

    return true;
}

// Provide next steps
function showNextSteps() {
    console.log('');
    console.log('🎯 Next Steps:');
    console.log('');
    console.log('1. Fix CORS Configuration:');
    console.log('   Windows:  fix-cors.bat');
    console.log('   Linux/Mac: ./fix-cors.sh');
    console.log('   PowerShell: .\\fix-cors.ps1');
    console.log('');
    console.log('2. Start Liquid Audio Agent:');
    console.log('   npm run dev');
    console.log('');
    console.log('3. Test the connection:');
    console.log('   - Open http://localhost:3000');
    console.log('   - Click Settings and configure N8N');
    console.log('   - Test the connection');
    console.log('');
    console.log('4. Run the test script (optional):');
    console.log('   node test-cors-connection.js <n8n-url> <api-key>');
    console.log('');
    console.log('📚 For detailed information, see: CORS-SOLUTION.md');
}

// Main validation
function runValidation() {
    const results = {
        files: checkFiles(),
        node: checkNodeAndNpm(),
        n8n: checkN8N(),
        react: checkReactDependencies(),
        processes: checkRunningProcesses()
    };

    console.log('');
    console.log('📊 Validation Results:');
    console.log(`   Required Files: ${results.files ? '✅' : '❌'}`);
    console.log(`   Node.js/npm: ${results.node ? '✅' : '❌'}`);
    console.log(`   n8n: ${results.n8n ? '✅' : '❌'}`);
    console.log(`   React Dependencies: ${results.react ? '✅' : '❌'}`);

    const criticalIssues = !results.files || !results.node || !results.react;
    const optionalIssues = !results.n8n;

    console.log('');

    if (criticalIssues) {
        console.log('❌ Critical issues found. Please fix them before proceeding.');
        process.exit(1);
    } else if (optionalIssues) {
        console.log('⚠️  Some optional components are missing. Setup can continue but may need additional steps.');
    } else {
        console.log('✅ All critical components are ready!');
    }

    showNextSteps();
}

// Run validation
if (require.main === module) {
    runValidation().catch(error => {
        console.error('❌ Validation failed:', error.message);
        process.exit(1);
    });
}

module.exports = { runValidation };