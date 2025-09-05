import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface ExtensionConfig {
  recommendations: string[];
  unwantedRecommendations?: string[];
}

export class ExtensionsManager {
  async getInstalledExtensions(): Promise<string[]> {
    return vscode.extensions.all
      .filter(ext => !ext.packageJSON.isBuiltin)
      .map(ext => ext.id);
  }

  async getExtensionStatus(extensionId: string): Promise<'installed' | 'not-installed' | 'disabled'> {
    const extension = vscode.extensions.getExtension(extensionId);
    
    if (!extension) {
      return 'not-installed';
    }
    
    return extension.isActive ? 'installed' : 'disabled';
  }

  async recommendExtension(extensionId: string): Promise<void> {
    const status = await this.getExtensionStatus(extensionId);
    
    if (status === 'not-installed') {
      const install = await vscode.window.showInformationMessage(
        `팀에서 권장하는 확장 '${extensionId}'를 설치하시겠습니까?`,
        '설치',
        '나중에'
      );
      
      if (install === '설치') {
        await this.installExtension(extensionId);
      }
    }
  }

  private async installExtension(extensionId: string): Promise<void> {
    try {
      await vscode.commands.executeCommand('workbench.extensions.installExtension', extensionId);
      vscode.window.showInformationMessage(`확장 '${extensionId}' 설치 완료`);
    } catch (error) {
      vscode.window.showErrorMessage(`확장 설치 실패: ${error}`);
    }
  }

  async disableUnwantedExtension(extensionId: string): Promise<void> {
    const extension = vscode.extensions.getExtension(extensionId);
    
    if (extension && extension.isActive) {
      const disable = await vscode.window.showWarningMessage(
        `팀 정책에 따라 확장 '${extensionId}'를 비활성화해야 합니다.`,
        '비활성화',
        '무시'
      );
      
      if (disable === '비활성화') {
        try {
          await vscode.commands.executeCommand('workbench.extensions.action.disableWorkspace', extensionId);
          vscode.window.showInformationMessage(`확장 '${extensionId}' 비활성화 완료`);
        } catch (error) {
          vscode.window.showErrorMessage(`확장 비활성화 실패: ${error}`);
        }
      }
    }
  }

  async updateExtensionsJson(config: ExtensionConfig): Promise<void> {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) {
      vscode.window.showWarningMessage('워크스페이스를 찾을 수 없습니다. VS Code에서 폴더를 열어주세요.');
      return;
    }

    const extensionsPath = path.join(workspaceFolder.uri.fsPath, '.vscode', 'extensions.json');
    const vscodePath = path.dirname(extensionsPath);

    if (!fs.existsSync(vscodePath)) {
      fs.mkdirSync(vscodePath, { recursive: true });
    }

    fs.writeFileSync(extensionsPath, JSON.stringify(config, null, 2));
    vscode.window.showInformationMessage('확장 권장 목록이 업데이트되었습니다');
  }

  async processExtensionRecommendations(config: ExtensionConfig): Promise<void> {
    for (const extensionId of config.recommendations) {
      await this.recommendExtension(extensionId);
    }

    if (config.unwantedRecommendations) {
      for (const extensionId of config.unwantedRecommendations) {
        await this.disableUnwantedExtension(extensionId);
      }
    }
  }
}
