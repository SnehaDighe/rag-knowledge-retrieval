const express = require('express');
const cors = require('express-cors');
const bodyParser = require('body-parser');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const PORT = process.env.NODE_PORT || 3000;

// Middleware
app.use(morgan('combined'));
app.use(bodyParser.json());
app.use(cors());

// Routes
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'RAG Knowledge Retrieval System - Node.js'
  });
});

app.post('/api/query', (req, res) => {
  try {
    const { query, k = 5 } = req.body;

    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    // TODO: Integrate with knowledge retrieval service
    res.json({
      query: query,
      results: [],
      count: 0
    });
  } catch (error) {
    console.error('Error processing query:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/ingest', (req, res) => {
  try {
    // TODO: Process file uploads

    res.json({
      message: 'Files ingested successfully',
      count: 0
    });
  } catch (error) {
    console.error('Error ingesting files:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/status', (req, res) => {
  res.json({
    status: 'operational',
    documents_indexed: 0,
    embeddings_stored: 0
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: err.message });
});

// Start server
app.listen(PORT, () => {
  console.log(`RAG Knowledge Retrieval Server running on port ${PORT}`);
});
