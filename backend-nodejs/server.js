const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const morgan = require('morgan');
const axios = require('axios');
const multer = require('multer');
const FormData = require('form-data');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const app = express();
const PORT = process.env.NODE_PORT || 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://flask-api:5000';

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../data/documents');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  }
});

const upload = multer({
  storage: storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/plain' || path.extname(file.originalname) === '.txt') {
      cb(null, true);
    } else {
      cb(new Error('Only .txt files are allowed'));
    }
  }
});

// Middleware
app.use(morgan('combined'));
app.use(bodyParser.json());
app.use(cors());

// Routes
app.get('/health', async (req, res) => {
  try {
    const response = await axios.get(`${FLASK_URL}/health`);
    res.json({
      ...response.data,
      service: 'RAG Knowledge Retrieval System - Node.js Gateway'
    });
  } catch (error) {
    console.error('Flask health check failed:', error.message);
    res.status(503).json({
      status: 'unhealthy',
      service: 'RAG Knowledge Retrieval System - Node.js Gateway',
      flask_connection: 'failed'
    });
  }
});

// Authentication Routes
app.post('/auth/signup', async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_URL}/auth/signup`, req.body);
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error('Signup error:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to connect to Flask backend' });
    }
  }
});

app.post('/auth/login', async (req, res) => {
  try {
    const response = await axios.post(`${FLASK_URL}/auth/login`, req.body);
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error('Login error:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to connect to Flask backend' });
    }
  }
});

app.get('/auth/verify', async (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    const response = await axios.get(`${FLASK_URL}/auth/verify`, {
      headers: { Authorization: authHeader }
    });
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error('Token verification error:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to connect to Flask backend' });
    }
  }
});

app.post('/api/query', async (req, res) => {
  try {
    const { query, k = 5 } = req.body;

    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    const authHeader = req.headers.authorization;
    const response = await axios.post(`${FLASK_URL}/api/query`, { query, k }, {
      headers: { Authorization: authHeader }
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error querying Flask backend:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to connect to Flask backend' });
    }
  }
});

app.post('/api/ingest', upload.array('files'), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No files provided' });
    }

    // Forward files to Flask backend
    const formData = new FormData();
    req.files.forEach(file => {
      formData.append('files', fs.createReadStream(file.path), file.originalname);
    });

    const authHeader = req.headers.authorization;
    const response = await axios.post(`${FLASK_URL}/api/ingest`, formData, {
      headers: {
        ...formData.getHeaders(),
        'Content-Type': 'multipart/form-data',
        Authorization: authHeader
      }
    });

    res.json(response.data);
  } catch (error) {
    console.error('Error ingesting files:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Failed to connect to Flask backend' });
    }
  }
});

app.get('/api/status', async (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    const response = await axios.get(`${FLASK_URL}/api/status`, {
      headers: { Authorization: authHeader }
    });
    res.json({
      ...response.data,
      gateway: 'nodejs',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error getting status from Flask backend:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(503).json({
        status: 'flask_unavailable',
        gateway: 'nodejs',
        timestamp: new Date().toISOString()
      });
    }
  }
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
