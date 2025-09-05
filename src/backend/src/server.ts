import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { config } from 'dotenv';

// Load environment variables
config();

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());

// CORS configuration
app.use(cors({
  origin: ['http://localhost:3000', 'vscode-webview://*'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.'
  }
});
app.use('/api/', limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    service: 'teamsync-backend'
  });
});

// In-memory storage for demo (replace with database later)
const deviceCodes = new Map();
const userCodes = new Map();

// Device Flow endpoints
app.post('/api/v1/auth/device', (req, res) => {
  try {
    const { client_id } = req.body;
    
    if (!client_id || client_id !== 'vscode-extension') {
      return res.status(400).json({ error: 'invalid_client' });
    }
    
    // Generate device code and user code
    const deviceCode = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    const userCode = Math.random().toString(36).substring(2, 8).toUpperCase();
    
    // Store in memory (expires in 10 minutes)
    const deviceData = {
      user_code: userCode,
      client_id,
      created_at: Date.now(),
      status: 'pending',
      expires_at: Date.now() + (10 * 60 * 1000) // 10 minutes
    };
    
    deviceCodes.set(deviceCode, deviceData);
    userCodes.set(userCode, deviceCode);
    
    // Clean up expired codes
    setTimeout(() => {
      deviceCodes.delete(deviceCode);
      userCodes.delete(userCode);
    }, 10 * 60 * 1000);
    
    res.json({
      device_code: deviceCode,
      user_code: userCode,
      verification_uri: 'http://localhost:3000/device',
      expires_in: 600,
      interval: 5
    });
  } catch (error) {
    console.error('Device code generation error:', error);
    res.status(500).json({ error: 'internal_server_error' });
  }
});

app.post('/api/v1/auth/token', (req, res) => {
  try {
    const { grant_type, device_code } = req.body;
    
    if (grant_type !== 'device_code') {
      return res.status(400).json({ error: 'unsupported_grant_type' });
    }
    
    const deviceData = deviceCodes.get(device_code);
    if (!deviceData) {
      return res.status(400).json({ error: 'expired_token' });
    }
    
    if (Date.now() > deviceData.expires_at) {
      deviceCodes.delete(device_code);
      userCodes.delete(deviceData.user_code);
      return res.status(400).json({ error: 'expired_token' });
    }
    
    if (deviceData.status === 'pending') {
      return res.status(400).json({ error: 'authorization_pending' });
    }
    
    if (deviceData.status === 'approved') {
      // Generate tokens (simplified for demo)
      const accessToken = 'demo_access_token_' + Math.random().toString(36);
      const refreshToken = 'demo_refresh_token_' + Math.random().toString(36);
      
      // Clean up
      deviceCodes.delete(device_code);
      userCodes.delete(deviceData.user_code);
      
      res.json({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'Bearer',
        expires_in: 3600
      });
    } else {
      res.status(400).json({ error: 'access_denied' });
    }
  } catch (error) {
    console.error('Token request error:', error);
    res.status(500).json({ error: 'internal_server_error' });
  }
});

app.post('/api/v1/auth/device/approve', (req, res) => {
  try {
    const { user_code } = req.body;
    
    if (!user_code) {
      return res.status(400).json({ error: 'invalid_request' });
    }
    
    const deviceCode = userCodes.get(user_code);
    if (!deviceCode) {
      return res.status(400).json({ error: 'invalid_user_code' });
    }
    
    const deviceData = deviceCodes.get(deviceCode);
    if (!deviceData) {
      return res.status(400).json({ error: 'expired_token' });
    }
    
    if (Date.now() > deviceData.expires_at) {
      deviceCodes.delete(deviceCode);
      userCodes.delete(user_code);
      return res.status(400).json({ error: 'expired_token' });
    }
    
    // Approve the device
    deviceData.status = 'approved';
    deviceData.approved_at = Date.now();
    deviceCodes.set(deviceCode, deviceData);
    
    res.json({
      success: true,
      message: 'Device approved successfully'
    });
  } catch (error) {
    console.error('Device approval error:', error);
    res.status(500).json({ error: 'internal_server_error' });
  }
});

// Teams API (simplified for demo)
app.get('/api/v1/teams', (req, res) => {
  // Mock teams data
  const teams = [
    {
      id: 'team-1',
      name: 'Frontend Team',
      description: 'React and TypeScript development team',
      memberRole: 'admin',
      joinedAt: new Date().toISOString()
    },
    {
      id: 'team-2', 
      name: 'Backend Team',
      description: 'Node.js and API development team',
      memberRole: 'member',
      joinedAt: new Date().toISOString()
    }
  ];
  
  res.json(teams);
});

// Configuration sync endpoints (simplified for demo)
app.post('/api/v1/configurations/sync', (req, res) => {
  try {
    const { teamId, configuration } = req.body;
    
    console.log('Configuration sync request:', { teamId, configuration });
    
    res.json({
      success: true,
      message: 'Configuration synced successfully',
      version: '1.0.0'
    });
  } catch (error) {
    console.error('Configuration sync error:', error);
    res.status(500).json({ error: 'internal_server_error' });
  }
});

app.get('/api/v1/configurations/teams/:teamId/latest', (req, res) => {
  try {
    const { teamId } = req.params;
    
    // Mock configuration data
    const configuration = {
      id: 'config-1',
      teamId,
      configuration: {
        settings: {
          'editor.fontSize': 14,
          'editor.tabSize': 2,
          'editor.insertSpaces': true,
          'files.autoSave': 'afterDelay'
        },
        extensions: [
          'ms-vscode.vscode-typescript-next',
          'esbenp.prettier-vscode',
          'ms-vscode.vscode-eslint'
        ],
        keybindings: [],
        snippets: {}
      },
      version: '1.0.0',
      createdAt: new Date().toISOString()
    };
    
    res.json(configuration);
  } catch (error) {
    console.error('Configuration fetch error:', error);
    res.status(500).json({ error: 'internal_server_error' });
  }
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.originalUrl} not found`
  });
});

// Error handler
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
  });
});

app.listen(PORT, () => {
  console.log(`🚀 TeamSync Backend running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
});

export default app;
