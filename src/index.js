import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import express from 'express';
import mysql from 'mysql2';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const scansDir = path.join(__dirname, 'scans');
const outputDir = path.join(__dirname, '..', 'output');
const logsDir = path.join(__dirname, '..', 'logs');

console.log('MerbanHub OCR Indexer initialized.');
console.log(`Scans Directory: ${scansDir}`);
console.log(`Output Directory: ${outputDir}`);
console.log(`Logs Directory: ${logsDir}`);

// MySQL connection setup
const db = mysql.createConnection({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'merbanhub'
});

db.connect((err) => {
  if (err) {
    console.error('MySQL connection error:', err);
  } else {
    console.log('Connected to MySQL database!');
  }
});

const app = express();

app.get('/', (_req, res) => res.send('OCR Indexer is alive'));

const port = process.env.PORT ?? 3000;
app.listen(port, () => console.log(`Listening on ${port}`));

// Add your OCR logic here in future…
