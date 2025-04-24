module.exports = {
  transformIgnorePatterns: [
    "/node_modules/(?!(react-vis-network-graph|vis-network)/)",
  ],
  moduleNameMapper: {
    "\\.(css|svg)$": "<rootDir>/src/__mocks__/fileMock.js",
  },
};
