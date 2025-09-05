import * as vscode from 'vscode';

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  owner_id: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface Bookmark {
  id: string;
  user_id: string;
  setting_id: string;
  name: string;
  description?: string;
  tags: string[];
  created_at: string;
}

export interface SyncRequest {
  settings: Record<string, any>;
}

export interface SyncResponse {
  success: boolean;
  applied_count: number;
  version: number;
  version_id: string;
}

export class ExtensionApiClient {
  private readonly API_BASE_URL = 'http://localhost:8000';
  private context: vscode.ExtensionContext;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
  }

  private async getAuthToken(): Promise<string | null> {
    const tokens = this.context.globalState.get<AuthTokens>('authTokens');
    if (!tokens || Date.now() > tokens.expiresAt) {
      return null;
    }
    return tokens.accessToken;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = await this.getAuthToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json() as Promise<T>;
  }

  // Authentication
  async login(email: string, password: string): Promise<{
    access_token: string;
    token_type: string;
    user: any;
  }> {
    const response = await this.makeRequest<{
      access_token: string;
      token_type: string;
      user: UserProfile;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });

    const tokens: AuthTokens = {
      accessToken: response.access_token,
      refreshToken: 'mock_refresh_token',
      expiresAt: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
    };

    await this.context.globalState.update('authTokens', tokens);
    return response;
  }

  async register(email: string, password: string, name: string): Promise<void> {
    await this.makeRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name })
    });
  }

  // User Profile
  async getMyProfile(): Promise<UserProfile> {
    return this.makeRequest<UserProfile>('/users/me');
  }

  async updateMyProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return this.makeRequest<UserProfile>('/users/me', {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  // Teams (for selection only)
  async getMyTeams(): Promise<Team[]> {
    return this.makeRequest<Team[]>('/teams');
  }

  // Settings Sync
  async syncApply(settings: Record<string, any>): Promise<SyncResponse> {
    return this.makeRequest<SyncResponse>('/settings/sync/apply', {
      method: 'POST',
      body: JSON.stringify({ settings })
    });
  }

  async syncPreview(settings: Record<string, any>): Promise<any> {
    return this.makeRequest('/settings/sync/preview', {
      method: 'POST',
      body: JSON.stringify({ settings })
    });
  }

  // Bookmarks
  async getBookmarks(): Promise<Bookmark[]> {
    return this.makeRequest<Bookmark[]>('/bookmarks');
  }

  async createBookmark(data: {
    setting_id: string;
    name: string;
    description?: string;
    tags?: string[];
  }): Promise<Bookmark> {
    return this.makeRequest<Bookmark>('/bookmarks', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async deleteBookmark(bookmarkId: string): Promise<void> {
    await this.makeRequest(`/bookmarks/${bookmarkId}`, {
      method: 'DELETE'
    });
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.makeRequest('/health');
  }
}
