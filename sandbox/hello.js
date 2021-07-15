const fs = require('fs');


console.log(process.cwd())
fs.writeFileSync('output.txt', 'Hello World');