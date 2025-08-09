module.exports = {
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '\\.(css)$': 'identity-obj-proxy'
  },
  transform: {
    '^.+\\.[tj]sx?$': 'babel-jest'
  }
};
