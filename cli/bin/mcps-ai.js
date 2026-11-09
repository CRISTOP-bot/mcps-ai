#!/usr/bin/env node
const { main } = require('../src/main');
main(process.argv.slice(2)).catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
