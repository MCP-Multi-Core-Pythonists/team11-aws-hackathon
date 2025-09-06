import { CursorSettings } from './cursorSettings';
import * as vscode from 'vscode';
import * as http from 'http';
import { URL } from 'url';

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
  };
}

export class ApiService {
  private baseUrl = 'https://l7ycatge3j.execute-api.us-east-1.amazonaws.com';
  private token: string | null = null;
  private cognitoConfig = {
    domain: 'https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com',
    clientId: '7n568rmtbtp2tt8m0av2hl0f2n',
    redirectUri: 'http://localhost:3000/callback',
    tokenEndpoint: 'https://sync-hub-851725240440.auth.us-east-1.amazoncognito.com/oauth2/token'
  };

  setToken(token: string) {
    this.token = token;
  }

  async login(): Promise<AuthResponse> {
    return new Promise((resolve, reject) => {
      const server = http.createServer(async (req, res) => {
        if (req.url?.startsWith('/callback')) {
          const url = new URL(req.url, 'http://localhost:3000');
          const code = url.searchParams.get('code');
          
          if (code) {
            try {
              const tokens = await this.exchangeCodeForTokens(code);
              const userInfo = await this.getUserInfo(tokens.access_token);
              
              const authResponse: AuthResponse = {
                token: tokens.access_token,
                user: {
                  id: userInfo.sub,
                  email: userInfo.email
                }
              };
              
              this.setToken(tokens.access_token);
              
              res.writeHead(200, { 'Content-Type': 'text/html' });
              res.end('<h1>Login successful! You can close this window.</h1>');
              server.close();
              resolve(authResponse);
            } catch (error) {
              res.writeHead(500, { 'Content-Type': 'text/html' });
              res.end('<h1>Login failed</h1>');
              server.close();
              reject(error);
            }
          } else {
            res.writeHead(400, { 'Content-Type': 'text/html' });
            res.end('<h1>No authorization code received</h1>');
            server.close();
            reject(new Error('No authorization code received'));
          }
        }
      });

      server.listen(3000, () => {
        const authUrl = `${this.cognitoConfig.domain}/login?client_id=${this.cognitoConfig.clientId}&response_type=code&scope=email+openid+profile&redirect_uri=${encodeURIComponent(this.cognitoConfig.redirectUri)}&identity_provider=Google`;
        vscode.env.openExternal(vscode.Uri.parse(authUrl));
      });
    });
  }

  private async exchangeCodeForTokens(code: string): Promise<any> {
    const https = require('https');
    const querystring = require('querystring');
    
    const postData = querystring.stringify({
      grant_type: 'authorization_code',
      client_id: this.cognitoConfig.clientId,
      code: code,
      redirect_uri: this.cognitoConfig.redirectUri,
    });

    return new Promise((resolve, reject) => {
      const options = {
        hostname: 'sync-hub-851725240440.auth.us-east-1.amazoncognito.com',
        port: 443,
        path: '/oauth2/token',
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Content-Length': Buffer.byteLength(postData)
        }
      };

      const req = https.request(options, (res: any) => {
        let data = '';
        res.on('data', (chunk: any) => data += chunk);
        res.on('end', () => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(data));
          } else {
            reject(new Error('Failed to exchange code for tokens'));
          }
        });
      });

      req.on('error', reject);
      req.write(postData);
      req.end();
    });
  }

  private async getUserInfo(accessToken: string): Promise<any> {
    const https = require('https');
    
    return new Promise((resolve, reject) => {
      const options = {
        hostname: 'sync-hub-851725240440.auth.us-east-1.amazoncognito.com',
        port: 443,
        path: '/oauth2/userInfo',
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        }
      };

      const req = https.request(options, (res: any) => {
        let data = '';
        res.on('data', (chunk: any) => data += chunk);
        res.on('end', () => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(data));
          } else {
            reject(new Error('Failed to get user info'));
          }
        });
      });

      req.on('error', reject);
      req.end();
    });
  }

  async pushSettings(settings: CursorSettings, isPublic: boolean): Promise<{ id: string; message: string }> {
    if (!this.token) {
      throw new Error('Not authenticated. Please login first.');
    }

    const settingsToUpload = [
      { name: 'settings.json', value: JSON.stringify(settings.settings) },
      { name: 'argv.json', value: JSON.stringify(settings.argv) },
      { name: 'mcp.json', value: JSON.stringify(settings.mcp) },
      { name: 'extensions.json', value: JSON.stringify(settings.extensions) }
    ];

    const results = [];
    
    for (const setting of settingsToUpload) {
      try {
        const response = await this.makeApiCall('/settings', 'POST', {
          name: setting.name,
          value: setting.value,
          is_public: isPublic
        });
        results.push(response);
      } catch (error) {
        throw new Error(`Failed to upload ${setting.name}: ${error}`);
      }
    }

    return {
      id: 'batch-' + Date.now(),
      message: `Successfully uploaded ${results.length} settings files`
    };
  }

  private async makeApiCall(endpoint: string, method: string, body?: any): Promise<any> {
    const https = require('https');
    const url = new URL(endpoint, this.baseUrl);
    
    const postData = body ? JSON.stringify(body) : undefined;
    
    return new Promise((resolve, reject) => {
      const options = {
        hostname: url.hostname,
        port: 443,
        path: url.pathname,
        method: method,
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
          ...(postData && { 'Content-Length': Buffer.byteLength(postData) })
        }
      };

      const req = https.request(options, (res: any) => {
        let data = '';
        res.on('data', (chunk: any) => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data ? JSON.parse(data) : {});
          } else {
            reject(new Error(`API call failed with status ${res.statusCode}: ${data}`));
          }
        });
      });

      req.on('error', reject);
      if (postData) {
        req.write(postData);
      }
      req.end();
    });
  }

  async pullSettings(): Promise<CursorSettings> {
    if (!this.token) {
      throw new Error('Not authenticated. Please login first.');
    }

    try {
      const response = await this.makeApiCall('/settings', 'GET');
      
      // 서버 응답을 CursorSettings 형태로 변환
      const cursorSettings: CursorSettings = {
        settings: {},
        argv: {},
        mcp: {},
        extensions: {}
      };

      if (response.settings && Array.isArray(response.settings)) {
        for (const setting of response.settings) {
          const fileName = setting.name;
          const content = setting.content;
          
          // 파일명에 따라 적절한 키에 매핑
          if (fileName === 'settings.json') {
            cursorSettings.settings = content;
          } else if (fileName === 'argv.json') {
            cursorSettings.argv = content;
          } else if (fileName === 'mcp.json') {
            cursorSettings.mcp = content;
          } else if (fileName === 'extensions.json') {
            cursorSettings.extensions = content;
          }
        }
      }

      return cursorSettings;
    } catch (error) {
      throw new Error(`Failed to pull settings: ${error}`);
    }
  }
}
