#!/usr/bin/env node
/**
 * Liquid Audio Agent Python Dependencies Installer
 * Node.js wrapper script that detects the platform and runs the appropriate installer
 */

import { spawn, execSync } from 'child_process';
import { platform } from 'os';
import { existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const isWindows = platform() === 'win32';
const isMac = platform() === 'darwin';
const isLinux = platform() === 'linux';

console.log('========================================');
console.log('Liquid Audio Agent Python Dependencies Installer');
console.log('========================================');
console.log();
console.log(`Detected platform: ${platform()}`);
console.log();

// Function to run command and show output
function runCommand(command, args, options = {}) {
    return new Promise((resolve, reject) => {
        console.log(`Running: ${command} ${args.join(' ')}`);
        console.log();

        const child = spawn(command, args, {
            stdio: 'inherit',
            ...options
        });

        child.on('close', (code) => {
            if (code === 0) {
                resolve(code);
            } else {
                reject(new Error(`Command failed with exit code ${code}`));
            }
        });

        child.on('error', (error) => {
            reject(error);
        });
    });
}

// Function to check if Python is available
function checkPython() {
    try {
        const version = execSync('python --version', { encoding: 'utf8' });
        console.log(`Python found: ${version.trim()}`);
        return 'python';
    } catch (error) {
        try {
            const version = execSync('python3 --version', { encoding: 'utf8' });
            console.log(`Python3 found: ${version.trim()}`);
            return 'python3';
        } catch (error3) {
            console.error('Python is not installed or not in PATH');
            console.error('Please install Python 3.12+ from https://www.python.org/');
            process.exit(1);
        }
    }
}

// Main installation function
async function installDependencies() {
    const projectRoot = join(__dirname, '..');

    try {
        // Check Python availability
        const pythonCmd = checkPython();
        console.log();

        // Determine which installer script to run
        let installerScript;
        let installerArgs = [];

        if (isWindows) {
            installerScript = join(projectRoot, 'install-python-deps.bat');
            // On Windows, we can just run the batch file directly
            installerArgs = [];
        } else {
            installerScript = join(projectRoot, 'install-python-deps.sh');
            installerArgs = [];

            // Make sure the shell script is executable
            try {
                execSync(`chmod +x "${installerScript}"`);
            } catch (error) {
                console.warn('Could not make script executable, trying anyway...');
            }
        }

        // Check if installer script exists
        if (!existsSync(installerScript)) {
            console.error(`Installer script not found: ${installerScript}`);
            console.error('Please make sure the installer script is in the project root');
            process.exit(1);
        }

        console.log(`Using installer: ${installerScript}`);
        console.log();

        // Run the appropriate installer
        if (isWindows) {
            await runCommand('cmd', ['/c', installerScript], {
                cwd: projectRoot
            });
        } else {
            await runCommand('bash', [installerScript], {
                cwd: projectRoot
            });
        }

        console.log();
        console.log('========================================');
        console.log('Installation completed successfully!');
        console.log('========================================');
        console.log();
        console.log('Next steps:');
        console.log('1. Check the installation summary above');
        console.log('2. If any packages failed, review the error messages');
        console.log('3. Run verification: npm run verify-python-setup');
        console.log('4. Start the application: npm run dev');
        console.log();

    } catch (error) {
        console.error();
        console.error('========================================');
        console.error('Installation failed!');
        console.error('========================================');
        console.error();
        console.error('Error:', error.message);
        console.log();
        console.log('Troubleshooting steps:');
        console.log('1. Make sure Python 3.12+ is installed and in PATH');
        console.log('2. Check that you have sufficient disk space');
        console.log('3. Try running the installer script directly:');
        console.log(`   ${isWindows ? 'install-python-deps.bat' : './install-python-deps.sh'}`);
        console.log('4. Review the error messages above for specific issues');
        console.log();
        process.exit(1);
    }
}

// Show platform-specific recommendations
function showPlatformRecommendations() {
    console.log('Platform-specific recommendations:');
    console.log();

    if (isWindows) {
        console.log('Windows:');
        console.log('- Install Python 3.12+ from python.org');
        console.log('- Install CUDA toolkit for GPU acceleration');
        console.log('- Consider using Windows Terminal for better output');
        console.log('- Run Command Prompt as Administrator if needed');
    } else if (isMac) {
        console.log('macOS:');
        console.log('- Install Python 3.12+ with Homebrew: brew install python@3.12');
        console.log('- Install Xcode Command Line Tools: xcode-select --install');
        console.log('- For GPU support, ensure NVIDIA drivers are installed');
    } else if (isLinux) {
        console.log('Linux:');
        console.log('- Install Python 3.12+ with package manager');
        console.log('  Ubuntu/Debian: sudo apt install python3.12 python3.12-venv python3.12-pip');
        console.log('  Fedora: sudo dnf install python3.12 python3.12-pip');
        console.log('- Install build tools: sudo apt install build-essential');
        console.log('- Install CUDA toolkit for GPU acceleration');
    }
    console.log();
}

// Main execution
if (import.meta.url === `file://${process.argv[1]}`) {
    showPlatformRecommendations();
    installDependencies();
}

export { installDependencies, checkPython };