import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { AuthProvider } from '../auth/authProvider';
import { Logger } from '../utils/logger';

interface ConfigurationData {
    settings?: any;
    keybindings?: any[];
    extensions?: string[];
    snippets?: Record<string, any>;
}

interface SyncResult {
    success: boolean;
    message: string;
    conflicts?: any[];
}

export class SyncEngine {
    private context: vscode.ExtensionContext;
    private authProvider: AuthProvider;
    private autoSyncTimer?: NodeJS.Timeout;
    private readonly API_BASE_URL = 'https://api.teamsync.dev';

    constructor(context: vscode.ExtensionContext, authProvider: AuthProvider) {
        this.context = context;
        this.authProvider = authProvider;
    }

    async syncToRemote(): Promise<SyncResult> {
        try {
            Logger.info('원격 동기화 시작');

            const accessToken = await this.authProvider.getAccessToken();
            if (!accessToken) {
                return {
                    success: false,
                    message: '인증이 필요합니다. 먼저 로그인해주세요.'
                };
            }

            // 로컬 설정 수집
            const localConfig = await this.collectLocalConfiguration();
            
            // 현재 팀 ID 가져오기
            const teamId = await this.getCurrentTeamId();
            if (!teamId) {
                return {
                    success: false,
                    message: '팀을 선택해주세요.'
                };
            }

            // 서버로 업로드
            const response = await fetch(`${this.API_BASE_URL}/api/v1/configurations/sync`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({
                    teamId,
                    configuration: localConfig
                })
            });

            if (!response.ok) {
                const error = await response.json();
                return {
                    success: false,
                    message: error.message || '동기화 실패'
                };
            }

            const result = await response.json();
            Logger.info('원격 동기화 완료');

            return {
                success: true,
                message: '설정이 성공적으로 동기화되었습니다.'
            };
        } catch (error) {
            Logger.error('원격 동기화 실패:', error);
            return {
                success: false,
                message: `동기화 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
            };
        }
    }

    async syncFromRemote(): Promise<SyncResult> {
        try {
            Logger.info('원격에서 설정 가져오기 시작');

            const accessToken = await this.authProvider.getAccessToken();
            if (!accessToken) {
                return {
                    success: false,
                    message: '인증이 필요합니다. 먼저 로그인해주세요.'
                };
            }

            const teamId = await this.getCurrentTeamId();
            if (!teamId) {
                return {
                    success: false,
                    message: '팀을 선택해주세요.'
                };
            }

            // 원격 설정 가져오기
            const response = await fetch(`${this.API_BASE_URL}/api/v1/configurations/teams/${teamId}/latest`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                return {
                    success: false,
                    message: error.message || '설정 가져오기 실패'
                };
            }

            const remoteConfig = await response.json();
            
            // 로컬에 적용
            await this.applyConfiguration(remoteConfig.configuration);
            
            Logger.info('원격 설정 적용 완료');

            return {
                success: true,
                message: '원격 설정이 성공적으로 적용되었습니다.'
            };
        } catch (error) {
            Logger.error('원격 설정 가져오기 실패:', error);
            return {
                success: false,
                message: `설정 가져오기 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`
            };
        }
    }

    async startAutoSync(): Promise<void> {
        const config = vscode.workspace.getConfiguration('teamsync');
        const autoSync = config.get<boolean>('autoSync', true);
        const interval = config.get<number>('syncInterval', 300) * 1000; // 초를 밀리초로 변환

        if (!autoSync) {
            Logger.info('자동 동기화가 비활성화되어 있습니다.');
            return;
        }

        this.stopAutoSync();

        this.autoSyncTimer = setInterval(async () => {
            try {
                Logger.info('자동 동기화 실행');
                await this.syncToRemote();
            } catch (error) {
                Logger.error('자동 동기화 실패:', error);
            }
        }, interval);

        Logger.info(`자동 동기화 시작 (간격: ${interval / 1000}초)`);
    }

    stopAutoSync(): void {
        if (this.autoSyncTimer) {
            clearInterval(this.autoSyncTimer);
            this.autoSyncTimer = undefined;
            Logger.info('자동 동기화 중지');
        }
    }

    private async collectLocalConfiguration(): Promise<ConfigurationData> {
        const config: ConfigurationData = {};

        try {
            // VS Code 설정 수집
            const workspaceConfig = vscode.workspace.getConfiguration();
            config.settings = {};
            
            // 주요 설정들만 수집 (전체 설정은 너무 많음)
            const importantSettings = [
                'editor.fontSize',
                'editor.fontFamily',
                'editor.tabSize',
                'editor.insertSpaces',
                'editor.wordWrap',
                'editor.minimap.enabled',
                'workbench.colorTheme',
                'workbench.iconTheme'
            ];

            for (const setting of importantSettings) {
                const value = workspaceConfig.get(setting);
                if (value !== undefined) {
                    config.settings[setting] = value;
                }
            }

            // 설치된 확장 목록
            config.extensions = vscode.extensions.all
                .filter(ext => !ext.packageJSON.isBuiltin)
                .map(ext => ext.id);

            // 키바인딩 (사용자 정의만)
            const keybindingsPath = this.getKeybindingsPath();
            if (keybindingsPath && fs.existsSync(keybindingsPath)) {
                const keybindingsContent = fs.readFileSync(keybindingsPath, 'utf8');
                try {
                    config.keybindings = JSON.parse(keybindingsContent);
                } catch (error) {
                    Logger.warn('키바인딩 파일 파싱 실패:', error);
                }
            }

            Logger.info('로컬 설정 수집 완료');
        } catch (error) {
            Logger.error('로컬 설정 수집 실패:', error);
        }

        return config;
    }

    private async applyConfiguration(config: ConfigurationData): Promise<void> {
        try {
            // VS Code 설정 적용
            if (config.settings) {
                const workspaceConfig = vscode.workspace.getConfiguration();
                
                for (const [key, value] of Object.entries(config.settings)) {
                    await workspaceConfig.update(key, value, vscode.ConfigurationTarget.Global);
                }
            }

            // 확장 설치 권장
            if (config.extensions && config.extensions.length > 0) {
                const installedExtensions = vscode.extensions.all.map(ext => ext.id);
                const missingExtensions = config.extensions.filter(ext => !installedExtensions.includes(ext));
                
                if (missingExtensions.length > 0) {
                    const result = await vscode.window.showInformationMessage(
                        `${missingExtensions.length}개의 확장을 설치하시겠습니까?`,
                        '설치',
                        '나중에'
                    );
                    
                    if (result === '설치') {
                        for (const extensionId of missingExtensions) {
                            try {
                                await vscode.commands.executeCommand('workbench.extensions.installExtension', extensionId);
                            } catch (error) {
                                Logger.warn(`확장 설치 실패: ${extensionId}`, error);
                            }
                        }
                    }
                }
            }

            // 키바인딩 적용
            if (config.keybindings) {
                const keybindingsPath = this.getKeybindingsPath();
                if (keybindingsPath) {
                    fs.writeFileSync(keybindingsPath, JSON.stringify(config.keybindings, null, 2));
                }
            }

            Logger.info('설정 적용 완료');
        } catch (error) {
            Logger.error('설정 적용 실패:', error);
            throw error;
        }
    }

    private getKeybindingsPath(): string | null {
        const platform = process.platform;
        let configDir: string;

        switch (platform) {
            case 'win32':
                configDir = path.join(process.env.APPDATA || '', 'Code', 'User');
                break;
            case 'darwin':
                configDir = path.join(process.env.HOME || '', 'Library', 'Application Support', 'Code', 'User');
                break;
            case 'linux':
                configDir = path.join(process.env.HOME || '', '.config', 'Code', 'User');
                break;
            default:
                return null;
        }

        return path.join(configDir, 'keybindings.json');
    }

    private async getCurrentTeamId(): Promise<string | null> {
        try {
            const teamId = await this.context.globalState.get<string>('teamsync.currentTeamId');
            return teamId || null;
        } catch (error) {
            Logger.error('현재 팀 ID 조회 실패:', error);
            return null;
        }
    }

    async setCurrentTeam(teamId: string): Promise<void> {
        await this.context.globalState.update('teamsync.currentTeamId', teamId);
        Logger.info(`현재 팀 설정: ${teamId}`);
    }
}
