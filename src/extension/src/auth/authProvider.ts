import * as vscode from 'vscode';
import { Logger } from '../utils/logger';

interface AuthTokens {
    accessToken: string;
    refreshToken: string;
    expiresAt: number;
}

interface DeviceCodeResponse {
    deviceCode: string;
    userCode: string;
    verificationUri: string;
    expiresIn: number;
    interval: number;
}

export class AuthProvider {
    private context: vscode.ExtensionContext;
    private readonly API_BASE_URL = 'https://api.teamsync.dev';

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    async login(): Promise<boolean> {
        try {
            Logger.info('로그인 프로세스 시작');

            // Device Code Flow 시작
            const deviceCode = await this.requestDeviceCode();
            
            // 사용자에게 인증 URL 표시
            const authUrl = `${deviceCode.verificationUri}?user_code=${deviceCode.userCode}`;
            
            const result = await vscode.window.showInformationMessage(
                `브라우저에서 인증을 완료해주세요.\n코드: ${deviceCode.userCode}`,
                '브라우저 열기',
                '취소'
            );

            if (result === '브라우저 열기') {
                await vscode.env.openExternal(vscode.Uri.parse(authUrl));
            } else {
                return false;
            }

            // 토큰 폴링
            const tokens = await this.pollForTokens(deviceCode.deviceCode, deviceCode.interval);
            
            if (tokens) {
                await this.saveTokens(tokens);
                vscode.window.showInformationMessage('TeamSync 로그인 성공!');
                
                // 인증 상태 컨텍스트 설정
                await vscode.commands.executeCommand('setContext', 'teamsync.authenticated', true);
                
                Logger.info('로그인 성공');
                return true;
            }

            return false;
        } catch (error) {
            Logger.error('로그인 실패:', error);
            vscode.window.showErrorMessage(`로그인 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
            return false;
        }
    }

    async logout(): Promise<void> {
        try {
            const tokens = await this.getTokens();
            
            if (tokens?.refreshToken) {
                // 서버에 토큰 무효화 요청
                await this.revokeToken(tokens.refreshToken);
            }

            // 로컬 토큰 삭제
            await this.clearTokens();
            
            // 인증 상태 컨텍스트 해제
            await vscode.commands.executeCommand('setContext', 'teamsync.authenticated', false);
            
            vscode.window.showInformationMessage('로그아웃되었습니다.');
            Logger.info('로그아웃 완료');
        } catch (error) {
            Logger.error('로그아웃 실패:', error);
            vscode.window.showErrorMessage('로그아웃 중 오류가 발생했습니다.');
        }
    }

    async isAuthenticated(): Promise<boolean> {
        const tokens = await this.getTokens();
        
        if (!tokens) {
            return false;
        }

        // 토큰 만료 확인
        if (Date.now() >= tokens.expiresAt) {
            // 토큰 갱신 시도
            const refreshed = await this.refreshTokens();
            return refreshed;
        }

        return true;
    }

    async getAccessToken(): Promise<string | null> {
        const tokens = await this.getTokens();
        
        if (!tokens) {
            return null;
        }

        // 토큰 만료 확인 및 갱신
        if (Date.now() >= tokens.expiresAt) {
            const refreshed = await this.refreshTokens();
            if (!refreshed) {
                return null;
            }
            
            // 갱신된 토큰 다시 가져오기
            const newTokens = await this.getTokens();
            return newTokens?.accessToken || null;
        }

        return tokens.accessToken;
    }

    private async requestDeviceCode(): Promise<DeviceCodeResponse> {
        const response = await fetch(`${this.API_BASE_URL}/auth/device`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                client_id: 'vscode-extension'
            })
        });

        if (!response.ok) {
            throw new Error('Device code 요청 실패');
        }

        return response.json();
    }

    private async pollForTokens(deviceCode: string, interval: number): Promise<AuthTokens | null> {
        const maxAttempts = 60; // 5분 (5초 * 60)
        let attempts = 0;

        return new Promise((resolve) => {
            const poll = async () => {
                attempts++;
                
                if (attempts > maxAttempts) {
                    resolve(null);
                    return;
                }

                try {
                    const response = await fetch(`${this.API_BASE_URL}/auth/token`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            grant_type: 'device_code',
                            device_code: deviceCode
                        })
                    });

                    if (response.ok) {
                        const tokens = await response.json();
                        resolve({
                            accessToken: tokens.access_token,
                            refreshToken: tokens.refresh_token,
                            expiresAt: Date.now() + (tokens.expires_in * 1000)
                        });
                        return;
                    }

                    // 아직 인증되지 않음, 계속 폴링
                    setTimeout(poll, interval * 1000);
                } catch (error) {
                    Logger.error('토큰 폴링 오류:', error);
                    setTimeout(poll, interval * 1000);
                }
            };

            poll();
        });
    }

    private async refreshTokens(): Promise<boolean> {
        try {
            const tokens = await this.getTokens();
            
            if (!tokens?.refreshToken) {
                return false;
            }

            const response = await fetch(`${this.API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: tokens.refreshToken
                })
            });

            if (!response.ok) {
                await this.clearTokens();
                return false;
            }

            const newTokens = await response.json();
            await this.saveTokens({
                accessToken: newTokens.access_token,
                refreshToken: newTokens.refresh_token,
                expiresAt: Date.now() + (newTokens.expires_in * 1000)
            });

            return true;
        } catch (error) {
            Logger.error('토큰 갱신 실패:', error);
            await this.clearTokens();
            return false;
        }
    }

    private async revokeToken(refreshToken: string): Promise<void> {
        try {
            await fetch(`${this.API_BASE_URL}/auth/revoke`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: refreshToken
                })
            });
        } catch (error) {
            Logger.error('토큰 무효화 실패:', error);
        }
    }

    private async saveTokens(tokens: AuthTokens): Promise<void> {
        await this.context.secrets.store('teamsync.tokens', JSON.stringify(tokens));
    }

    private async getTokens(): Promise<AuthTokens | null> {
        try {
            const tokensJson = await this.context.secrets.get('teamsync.tokens');
            return tokensJson ? JSON.parse(tokensJson) : null;
        } catch (error) {
            Logger.error('토큰 조회 실패:', error);
            return null;
        }
    }

    private async clearTokens(): Promise<void> {
        await this.context.secrets.delete('teamsync.tokens');
    }
}
