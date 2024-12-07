module.exports = {
  networks: {
    development: {
      host: "192.168.0.2",
      port: 8545,
      network_id: "*",
    },
  },
  contracts_directory: "./contracts",
  compilers: {
    solc: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },

  db: {
    enabled: false,
  },
};
