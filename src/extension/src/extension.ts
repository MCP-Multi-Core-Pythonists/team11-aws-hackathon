import * as vscode from 'vscode';
import { AuthProvider } from './auth/authProvider';
import { SyncEngine } from './sync/syncEngine';
import { registerCommands } from './ui/commands';
import { StatusBarManager } from './ui/statusBar';
import { Logger } from './utils/logger';

let authProvider: AuthProvider;
let syncEngine: SyncEngine;
let statusBarManager: StatusBarManager;

export async function activate(context: vscode.ExtensionContext) {
    Logger.info('TeamSync Pro 확장이 활성화되었습니다.');

    try {
        // 핵심 서비스 초기화
        authProvider = new AuthProvider(context);
        syncEngine = new SyncEngine(context, authProvider);
        statusBarManager = new StatusBarManager();

        // 명령어 등록
        registerCommands(context, authProvider, syncEngine);

        // 상태바 초기화
        statusBarManager.initialize();

        // 인증 상태 확인 및 자동 동기화 시작
        if (await authProvider.isAuthenticated()) {
            await syncEngine.startAutoSync();
            statusBarManager.setAuthenticated(true);
        }

        Logger.info('TeamSync Pro 초기화 완료');
    } catch (error) {
        Logger.error('TeamSync Pro 초기화 실패:', error);
        vscode.window.showErrorMessage('TeamSync Pro 초기화에 실패했습니다.');
    }
}

export function deactivate() {
    Logger.info('TeamSync Pro 확장이 비활성화되었습니다.');
    
    if (syncEngine) {
        syncEngine.stopAutoSync();
    }
    
    if (statusBarManager) {
        statusBarManager.dispose();
    }
}
