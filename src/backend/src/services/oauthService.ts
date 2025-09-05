import axios from 'axios';

interface OAuthUserInfo {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

export class OAuthService {
  private readonly googleConfig = {
    clientId: process.env.GOOGLE_CLIENT_ID!,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    redirectUri: process.env.GOOGLE_REDIRECT_URI!,
    tokenUrl: 'https://oauth2.googleapis.com/token',
    userInfoUrl: 'https://www.googleapis.com/oauth2/v2/userinfo'
  };

  private readonly githubConfig = {
    clientId: process.env.GITHUB_CLIENT_ID!,
    clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    redirectUri: process.env.GITHUB_REDIRECT_URI!,
    tokenUrl: 'https://github.com/login/oauth/access_token',
    userInfoUrl: 'https://api.github.com/user'
  };

  async exchangeCodeForUser(provider: string, code: string): Promise<OAuthUserInfo> {
    if (provider === 'google') {
      return this.handleGoogleAuth(code);
    } else if (provider === 'github') {
      return this.handleGithubAuth(code);
    }
    throw new Error('Unsupported OAuth provider');
  }

  private async handleGoogleAuth(code: string): Promise<OAuthUserInfo> {
    // 액세스 토큰 교환
    const tokenResponse = await axios.post(this.googleConfig.tokenUrl, {
      client_id: this.googleConfig.clientId,
      client_secret: this.googleConfig.clientSecret,
      code,
      grant_type: 'authorization_code',
      redirect_uri: this.googleConfig.redirectUri
    });

    const { access_token } = tokenResponse.data;

    // 사용자 정보 가져오기
    const userResponse = await axios.get(this.googleConfig.userInfoUrl, {
      headers: { Authorization: `Bearer ${access_token}` }
    });

    const userData = userResponse.data;
    return {
      id: userData.id,
      email: userData.email,
      name: userData.name,
      avatar: userData.picture
    };
  }

  private async handleGithubAuth(code: string): Promise<OAuthUserInfo> {
    // 액세스 토큰 교환
    const tokenResponse = await axios.post(this.githubConfig.tokenUrl, {
      client_id: this.githubConfig.clientId,
      client_secret: this.githubConfig.clientSecret,
      code
    }, {
      headers: { Accept: 'application/json' }
    });

    const { access_token } = tokenResponse.data;

    // 사용자 정보 가져오기
    const userResponse = await axios.get(this.githubConfig.userInfoUrl, {
      headers: { Authorization: `Bearer ${access_token}` }
    });

    const userData = userResponse.data;
    return {
      id: userData.id.toString(),
      email: userData.email,
      name: userData.name || userData.login,
      avatar: userData.avatar_url
    };
  }

  getAuthorizationUrl(provider: 'google' | 'github', redirectUri?: string, state?: string): string {
    if (provider === 'google') {
      const params = new URLSearchParams({
        client_id: this.googleConfig.clientId,
        redirect_uri: redirectUri || this.googleConfig.redirectUri,
        response_type: 'code',
        scope: 'openid email profile',
        ...(state && { state })
      });
      return `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
    } else if (provider === 'github') {
      const params = new URLSearchParams({
        client_id: this.githubConfig.clientId,
        redirect_uri: redirectUri || this.githubConfig.redirectUri,
        scope: 'user:email',
        ...(state && { state })
      });
      return `https://github.com/login/oauth/authorize?${params}`;
    }
    throw new Error('Unsupported OAuth provider');
  }
}
