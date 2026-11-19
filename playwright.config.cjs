const { defineConfig } = require('@playwright/test');

const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
module.exports = defineConfig({
  testDir: './tests/browser',
  fullyParallel: false,
  workers: 1,
  timeout: 240_000,
  expect: { timeout: 7_000 },
  retries: 0,
  reporter: [['list'], ['json', { outputFile: 'test-results/browser-results.json' }]],
  use: {
    baseURL: 'https://localhost:8123',
    ignoreHTTPSErrors: true,
    browserName: 'chromium',
    headless: true,
    viewport: { width: 1440, height: 1000 },
    trace: 'retain-on-failure',
    launchOptions: executablePath ? {
      executablePath,
      args: ['--no-sandbox', '--disable-dev-shm-usage'],
    } : {},
  },
  webServer: {
    command: 'python3 tests/browser_server.py',
    url: 'https://localhost:8123/__test/ready',
    ignoreHTTPSErrors: true,
    reuseExistingServer: false,
    timeout: 30_000,
    stdout: 'pipe',
  },
});
