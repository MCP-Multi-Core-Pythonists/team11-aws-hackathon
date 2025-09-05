// Types
export interface Team {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  owner_id: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  id: string;
  user_id: string;
  team_id: string;
  email: string;
  name: string;
  role: string;
  joined_at: string;
}

export interface TeamConfig {
  id: string;
  team_id: string;
  name: string;
  settings_json: Record<string, any>;
  created_by: string;
  created_at: string;
}

export interface Prompt {
  id: string;
  team_id: string;
  name: string;
  content: string;
  category: string;
  created_by: string;
  created_at: string;
}

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  message: string;
  read: boolean;
  created_at: string;
}

export interface Activity {
  id: string;
  user_id: string;
  team_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details: Record<string, any>;
  created_at: string;
}

export interface PromptCategory {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export class FrontendApiClient {
  private readonly API_BASE_URL = 'http://localhost:8000';
  private authToken: string | null = null;

  setAuthToken(token: string) {
    this.authToken = token;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    const response = await fetch(`${this.API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Authentication
  async login(email: string, password: string): Promise<{
    access_token: string;
    token_type: string;
    user: any;
  }> {
    return this.makeRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  async register(email: string, password: string, name: string): Promise<void> {
    await this.makeRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name })
    });
  }

  // Teams Management
  async getTeams(): Promise<Team[]> {
    return this.makeRequest<Team[]>('/teams');
  }

  async createTeam(data: {
    name: string;
    description?: string;
    is_public: boolean;
  }): Promise<Team> {
    return this.makeRequest<Team>('/teams', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async getTeamMembers(teamId: string): Promise<TeamMember[]> {
    return this.makeRequest<TeamMember[]>(`/teams/${teamId}/members`);
  }

  async inviteTeamMember(teamId: string, data: {
    email: string;
    role: string;
  }): Promise<void> {
    await this.makeRequest(`/teams/${teamId}/invite`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async removeTeamMember(teamId: string, userId: string): Promise<void> {
    await this.makeRequest(`/teams/${teamId}/members/${userId}`, {
      method: 'DELETE'
    });
  }

  // Team Configs
  async getTeamConfigs(teamId: string): Promise<TeamConfig[]> {
    return this.makeRequest<TeamConfig[]>(`/teams/${teamId}/configs`);
  }

  async createTeamConfig(teamId: string, data: {
    name: string;
    settings_json: Record<string, any>;
  }): Promise<TeamConfig> {
    return this.makeRequest<TeamConfig>(`/teams/${teamId}/configs`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateTeamConfig(teamId: string, configId: string, data: {
    name: string;
    settings_json: Record<string, any>;
  }): Promise<TeamConfig> {
    return this.makeRequest<TeamConfig>(`/teams/${teamId}/configs/${configId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteTeamConfig(teamId: string, configId: string): Promise<void> {
    await this.makeRequest(`/teams/${teamId}/configs/${configId}`, {
      method: 'DELETE'
    });
  }

  // Prompts
  async getTeamPrompts(teamId: string): Promise<Prompt[]> {
    return this.makeRequest<Prompt[]>(`/teams/${teamId}/prompts`);
  }

  async createTeamPrompt(teamId: string, data: {
    name: string;
    content: string;
    category: string;
  }): Promise<Prompt> {
    return this.makeRequest<Prompt>(`/teams/${teamId}/prompts`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateTeamPrompt(teamId: string, promptId: string, data: {
    name: string;
    content: string;
    category: string;
  }): Promise<Prompt> {
    return this.makeRequest<Prompt>(`/teams/${teamId}/prompts/${promptId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteTeamPrompt(teamId: string, promptId: string): Promise<void> {
    await this.makeRequest(`/teams/${teamId}/prompts/${promptId}`, {
      method: 'DELETE'
    });
  }

  // Notifications
  async getNotifications(): Promise<Notification[]> {
    return this.makeRequest<Notification[]>('/notifications');
  }

  async markNotificationRead(notificationId: string): Promise<void> {
    await this.makeRequest(`/notifications/${notificationId}/read`, {
      method: 'PUT'
    });
  }

  async deleteNotification(notificationId: string): Promise<void> {
    await this.makeRequest(`/notifications/${notificationId}`, {
      method: 'DELETE'
    });
  }

  // Activities
  async getTeamActivities(teamId: string): Promise<Activity[]> {
    return this.makeRequest<Activity[]>(`/teams/${teamId}/activities`);
  }

  async getMyActivities(): Promise<Activity[]> {
    return this.makeRequest<Activity[]>('/users/me/activities');
  }

  // Search
  async searchTeams(query: string, limit = 20): Promise<Team[]> {
    return this.makeRequest<Team[]>(`/search/teams?query=${encodeURIComponent(query)}&limit=${limit}`);
  }

  async searchPrompts(query: string, category?: string, teamId?: string, limit = 20): Promise<Prompt[]> {
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });
    
    if (category) params.append('category', category);
    if (teamId) params.append('team_id', teamId);

    return this.makeRequest<Prompt[]>(`/search/prompts?${params}`);
  }

  async searchConfigs(query: string, teamId?: string, limit = 20): Promise<TeamConfig[]> {
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });
    
    if (teamId) params.append('team_id', teamId);

    return this.makeRequest<TeamConfig[]>(`/search/configs?${params}`);
  }

  // Prompt Categories
  async getPromptCategories(): Promise<PromptCategory[]> {
    return this.makeRequest<PromptCategory[]>('/prompt-categories');
  }

  async createPromptCategory(data: {
    name: string;
    description?: string;
  }): Promise<PromptCategory> {
    return this.makeRequest<PromptCategory>('/prompt-categories', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
}

export const apiClient = new FrontendApiClient();
