module.exports = {
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '\\.(css)$': '<rootDir>/tests/styleMock.js'
  },
  setupFilesAfterEnv: ['@testing-library/jest-dom']
};
