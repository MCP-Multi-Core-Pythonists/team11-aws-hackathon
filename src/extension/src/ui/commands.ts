import * as vscode from 'vscode';
import { AuthProvider } from '../auth/authProvider';
import { SyncEngine } from '../sync/syncEngine';
import { Logger } from '../utils/logger';

export function registerCommands(
    context: vscode.ExtensionContext,
    authProvider: AuthProvider,
    syncEngine: SyncEngine
): void {
    // 로그인 명령어
    const loginCommand = vscode.commands.registerCommand('teamsync.login', async () => {
        const success = await authProvider.login();
        if (success) {
            await syncEngine.startAutoSync();
            // 상태바 업데이트를 위한 이벤트 발생
            vscode.commands.executeCommand('teamsync.updateStatusBar');
        }
    });

    // 로그아웃 명령어
    const logoutCommand = vscode.commands.registerCommand('teamsync.logout', async () => {
        await authProvider.logout();
        syncEngine.stopAutoSync();
        vscode.commands.executeCommand('teamsync.updateStatusBar');
    });

    // 원격으로 동기화 명령어
    const syncToRemoteCommand = vscode.commands.registerCommand('teamsync.syncToRemote', async () => {
        const isAuthenticated = await authProvider.isAuthenticated();
        if (!isAuthenticated) {
            vscode.window.showWarningMessage('먼저 로그인해주세요.');
            return;
        }

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: '설정을 원격으로 동기화 중...',
            cancellable: false
        }, async (progress) => {
            const result = await syncEngine.syncToRemote();
            
            if (result.success) {
                vscode.window.showInformationMessage(result.message);
            } else {
                vscode.window.showErrorMessage(result.message);
            }
        });
    });

    // 원격에서 가져오기 명령어
    const syncFromRemoteCommand = vscode.commands.registerCommand('teamsync.syncFromRemote', async () => {
        const isAuthenticated = await authProvider.isAuthenticated();
        if (!isAuthenticated) {
            vscode.window.showWarningMessage('먼저 로그인해주세요.');
            return;
        }

        const confirmation = await vscode.window.showWarningMessage(
            '원격 설정을 가져오면 현재 로컬 설정이 변경될 수 있습니다. 계속하시겠습니까?',
            '계속',
            '취소'
        );

        if (confirmation !== '계속') {
            return;
        }

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: '원격 설정을 가져오는 중...',
            cancellable: false
        }, async (progress) => {
            const result = await syncEngine.syncFromRemote();
            
            if (result.success) {
                vscode.window.showInformationMessage(result.message);
            } else {
                vscode.window.showErrorMessage(result.message);
            }
        });
    });

    // 팀 선택 명령어
    const selectTeamCommand = vscode.commands.registerCommand('teamsync.selectTeam', async () => {
        const isAuthenticated = await authProvider.isAuthenticated();
        if (!isAuthenticated) {
            vscode.window.showWarningMessage('먼저 로그인해주세요.');
            return;
        }

        try {
            const teams = await fetchUserTeams(authProvider);
            
            if (teams.length === 0) {
                vscode.window.showInformationMessage('참여 중인 팀이 없습니다. 웹 콘솔에서 팀을 생성하거나 초대를 받아보세요.');
                return;
            }

            const teamItems = teams.map(team => ({
                label: team.name,
                description: team.description || '',
                detail: `멤버 ${team.memberCount}명`,
                teamId: team.id
            }));

            const selectedTeam = await vscode.window.showQuickPick(teamItems, {
                placeHolder: '동기화할 팀을 선택하세요'
            });

            if (selectedTeam) {
                await syncEngine.setCurrentTeam(selectedTeam.teamId);
                vscode.window.showInformationMessage(`팀 '${selectedTeam.label}'이 선택되었습니다.`);
                vscode.commands.executeCommand('teamsync.updateStatusBar');
            }
        } catch (error) {
            Logger.error('팀 목록 조회 실패:', error);
            vscode.window.showErrorMessage('팀 목록을 가져오는데 실패했습니다.');
        }
    });

    // TeamSync 패널 열기 명령어
    const showPanelCommand = vscode.commands.registerCommand('teamsync.showPanel', async () => {
        const panel = vscode.window.createWebviewPanel(
            'teamsyncPanel',
            'TeamSync Pro',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = getWebviewContent();
        
        // 웹뷰 메시지 처리
        panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'login':
                    await vscode.commands.executeCommand('teamsync.login');
                    break;
                case 'logout':
                    await vscode.commands.executeCommand('teamsync.logout');
                    break;
                case 'syncToRemote':
                    await vscode.commands.executeCommand('teamsync.syncToRemote');
                    break;
                case 'syncFromRemote':
                    await vscode.commands.executeCommand('teamsync.syncFromRemote');
                    break;
                case 'selectTeam':
                    await vscode.commands.executeCommand('teamsync.selectTeam');
                    break;
            }
        });
    });

    // 상태바 업데이트 명령어 (내부용)
    const updateStatusBarCommand = vscode.commands.registerCommand('teamsync.updateStatusBar', () => {
        // 상태바 매니저에서 처리
    });

    // 컨텍스트에 명령어 등록
    context.subscriptions.push(
        loginCommand,
        logoutCommand,
        syncToRemoteCommand,
        syncFromRemoteCommand,
        selectTeamCommand,
        showPanelCommand,
        updateStatusBarCommand
    );

    Logger.info('모든 명령어가 등록되었습니다.');
}

async function fetchUserTeams(authProvider: AuthProvider): Promise<any[]> {
    const accessToken = await authProvider.getAccessToken();
    if (!accessToken) {
        throw new Error('인증 토큰이 없습니다.');
    }

    const response = await fetch('https://api.teamsync.dev/api/v1/teams', {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });

    if (!response.ok) {
        throw new Error('팀 목록 조회 실패');
    }

    return response.json();
}

function getWebviewContent(): string {
    return `
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TeamSync Pro</title>
        <style>
            body {
                font-family: var(--vscode-font-family);
                color: var(--vscode-foreground);
                background-color: var(--vscode-editor-background);
                padding: 20px;
                margin: 0;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .logo {
                font-size: 24px;
                font-weight: bold;
                color: var(--vscode-textLink-foreground);
                margin-bottom: 10px;
            }
            .subtitle {
                color: var(--vscode-descriptionForeground);
                font-size: 14px;
            }
            .section {
                margin-bottom: 30px;
                padding: 20px;
                border: 1px solid var(--vscode-panel-border);
                border-radius: 6px;
                background-color: var(--vscode-panel-background);
            }
            .section-title {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 15px;
                color: var(--vscode-foreground);
            }
            .button {
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .button:hover {
                background-color: var(--vscode-button-hoverBackground);
            }
            .button.secondary {
                background-color: var(--vscode-button-secondaryBackground);
                color: var(--vscode-button-secondaryForeground);
            }
            .button.secondary:hover {
                background-color: var(--vscode-button-secondaryHoverBackground);
            }
            .status {
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 15px;
                font-size: 13px;
            }
            .status.success {
                background-color: var(--vscode-inputValidation-infoBackground);
                border: 1px solid var(--vscode-inputValidation-infoBorder);
                color: var(--vscode-inputValidation-infoForeground);
            }
            .status.warning {
                background-color: var(--vscode-inputValidation-warningBackground);
                border: 1px solid var(--vscode-inputValidation-warningBorder);
                color: var(--vscode-inputValidation-warningForeground);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TeamSync Pro</div>
                <div class="subtitle">팀 개발 환경 설정 동기화 도구</div>
            </div>

            <div class="section">
                <div class="section-title">인증</div>
                <div class="status warning">
                    로그인이 필요합니다.
                </div>
                <button class="button" onclick="sendMessage('login')">로그인</button>
                <button class="button secondary" onclick="sendMessage('logout')">로그아웃</button>
            </div>

            <div class="section">
                <div class="section-title">팀 관리</div>
                <button class="button" onclick="sendMessage('selectTeam')">팀 선택</button>
            </div>

            <div class="section">
                <div class="section-title">동기화</div>
                <button class="button" onclick="sendMessage('syncToRemote')">원격으로 동기화</button>
                <button class="button secondary" onclick="sendMessage('syncFromRemote')">원격에서 가져오기</button>
            </div>
        </div>

        <script>
            const vscode = acquireVsCodeApi();
            
            function sendMessage(command) {
                vscode.postMessage({ command: command });
            }
        </script>
    </body>
    </html>
    `;
}
