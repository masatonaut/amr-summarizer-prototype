module.exports = {
  jest: {
    configure: {
      transformIgnorePatterns: [
        "<rootDir>/node_modules/(?!(react-vis-network-graph|vis-network)/)",
      ],
      moduleNameMapper: {
        "\\.(css|less|scss|sass)$": "identity-obj-proxy",
        "\\.(gif|ttf|eot|svg|png)$": "<rootDir>/src/__mocks__/fileMock.js",

        "^react-vis-network-graph$":
          "<rootDir>/src/__mocks__/react-vis-network-graph.js",
      },
    },
  },
};
