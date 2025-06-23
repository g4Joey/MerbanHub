const fs = require('fs');
const path = require('path');

const scansDir = path.join(__dirname, 'scans');
const outputDir = path.join(__dirname, '..', 'output');
const logsDir = path.join(__dirname, '..', 'logs');

console.log('MerbanHub OCR Indexer initialized.');
console.log(`Scans Directory: ${scansDir}`);
console.log(`Output Directory: ${outputDir}`);
console.log(`Logs Directory: ${logsDir}`);

require('dotenv').config();
const express = require('express');
const app = express();

app.get('/', (req, res) => res.send('OCR Indexer is alive'));
const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Listening on ${port}`));


// Add your OCR logic here in future
