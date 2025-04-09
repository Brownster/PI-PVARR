module.exports = {
  testEnvironment: 'jsdom',
  rootDir: './',
  moduleDirectories: ['node_modules', 'web-ui'],
  moduleFileExtensions: ['js', 'json'],
  testMatch: ['**/test/**/*.test.js'],
  transform: {},
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov'],
  coverageThreshold: {
    global: {
      statements: 70,
      branches: 60,
      functions: 70,
      lines: 70
    }
  },
  testEnvironmentOptions: {
    url: 'http://localhost/'
  },
  setupFiles: ['./test/setup.js']
};