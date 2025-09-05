# 006 - 기본 프롬프트 팔레트 UI

## 📋 개발 목표
팀에서 공유하는 프롬프트 템플릿을 쉽게 접근하고 사용할 수 있는 팔레트 UI를 구현합니다.

## 🎯 구현 범위
- 프롬프트 목록 표시
- 카테고리별 필터링
- 프롬프트 미리보기
- 클립보드 복사 기능

## 🛠️ 기술 스택
- VS Code QuickPick API
- TreeView Provider
- Webview Panel (선택사항)

## 📝 구현 단계

### 1단계: 프롬프트 데이터 모델
```typescript
// src/types/prompt.ts
export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  content: string;
  tags: string[];
  author?: string;
  createdAt?: Date;
}

export interface PromptCategory {
  id: string;
  name: string;
  description: string;
  prompts: PromptTemplate[];
}
```

### 2단계: 프롬프트 로더 서비스
```typescript
// src/services/promptLoader.ts
import * as fs from 'fs';
import * as path from 'path';
import { PromptTemplate, PromptCategory } from '../types/prompt';
import { TeamConfig } from '../types/config';

export class PromptLoader {
  async loadPrompts(configDir: string, teamConfig: TeamConfig): Promise<PromptTemplate[]> {
    const prompts: PromptTemplate[] = [];

    for (const promptConfig of teamConfig.prompts) {
      try {
        const promptPath = path.join(configDir, promptConfig.file);
        const content = fs.readFileSync(promptPath, 'utf8');
        
        const prompt: PromptTemplate = {
          id: promptConfig.name,
          name: this.extractTitle(content) || promptConfig.name,
          description: this.extractDescription(content) || '',
          category: promptConfig.category,
          content: content,
          tags: this.extractTags(content)
        };

        prompts.push(prompt);
      } catch (error) {
        console.error(`프롬프트 로드 실패: ${promptConfig.file}`, error);
      }
    }

    return prompts;
  }

  private extractTitle(content: string): string | null {
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return titleMatch ? titleMatch[1] : null;
  }

  private extractDescription(content: string): string {
    const descMatch = content.match(/^##\s+(.+)$/m);
    return descMatch ? descMatch[1] : '';
  }

  private extractTags(content: string): string[] {
    const tagMatch = content.match(/tags:\s*\[([^\]]+)\]/i);
    if (tagMatch) {
      return tagMatch[1].split(',').map(tag => tag.trim());
    }
    return [];
  }

  groupByCategory(prompts: PromptTemplate[]): PromptCategory[] {
    const categories = new Map<string, PromptTemplate[]>();

    prompts.forEach(prompt => {
      if (!categories.has(prompt.category)) {
        categories.set(prompt.category, []);
      }
      categories.get(prompt.category)!.push(prompt);
    });

    return Array.from(categories.entries()).map(([categoryId, prompts]) => ({
      id: categoryId,
      name: this.formatCategoryName(categoryId),
      description: `${prompts.length}개의 프롬프트`,
      prompts
    }));
  }

  private formatCategoryName(categoryId: string): string {
    const names: { [key: string]: string } = {
      'development': '개발',
      'review': '코드 리뷰',
      'testing': '테스트',
      'documentation': '문서화',
      'deployment': '배포'
    };
    return names[categoryId] || categoryId;
  }
}
```

### 3단계: QuickPick 기반 프롬프트 팔레트
```typescript
// src/ui/promptPalette.ts
import * as vscode from 'vscode';
import { PromptTemplate, PromptCategory } from '../types/prompt';

export class PromptPalette {
  async showPromptPalette(categories: PromptCategory[]): Promise<void> {
    // 1단계: 카테고리 선택
    const selectedCategory = await this.selectCategory(categories);
    if (!selectedCategory) return;

    // 2단계: 프롬프트 선택
    const selectedPrompt = await this.selectPrompt(selectedCategory.prompts);
    if (!selectedPrompt) return;

    // 3단계: 액션 선택
    await this.selectAction(selectedPrompt);
  }

  private async selectCategory(categories: PromptCategory[]): Promise<PromptCategory | undefined> {
    const items: vscode.QuickPickItem[] = categories.map(category => ({
      label: category.name,
      description: category.description,
      detail: `${category.prompts.length}개의 프롬프트`
    }));

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: '프롬프트 카테고리를 선택하세요'
    });

    if (selected) {
      return categories.find(c => c.name === selected.label);
    }
  }

  private async selectPrompt(prompts: PromptTemplate[]): Promise<PromptTemplate | undefined> {
    const items: vscode.QuickPickItem[] = prompts.map(prompt => ({
      label: prompt.name,
      description: prompt.description,
      detail: prompt.tags.join(', ')
    }));

    const selected = await vscode.window.showQuickPick(items, {
      placeHolder: '사용할 프롬프트를 선택하세요'
    });

    if (selected) {
      return prompts.find(p => p.name === selected.label);
    }
  }

  private async selectAction(prompt: PromptTemplate): Promise<void> {
    const actions = [
      { label: '📋 클립보드에 복사', action: 'copy' },
      { label: '👁️ 미리보기', action: 'preview' },
      { label: '📝 새 파일로 열기', action: 'newFile' }
    ];

    const selected = await vscode.window.showQuickPick(actions, {
      placeHolder: '수행할 작업을 선택하세요'
    });

    if (selected) {
      await this.executeAction(selected.action, prompt);
    }
  }

  private async executeAction(action: string, prompt: PromptTemplate): Promise<void> {
    switch (action) {
      case 'copy':
        await vscode.env.clipboard.writeText(prompt.content);
        vscode.window.showInformationMessage('프롬프트가 클립보드에 복사되었습니다');
        break;
      
      case 'preview':
        await this.showPreview(prompt);
        break;
      
      case 'newFile':
        await this.openAsNewFile(prompt);
        break;
    }
  }
}
```

### 4단계: 프롬프트 미리보기 기능
```typescript
// PromptPalette 클래스 내부 메서드
private async showPreview(prompt: PromptTemplate): Promise<void> {
  const panel = vscode.window.createWebviewPanel(
    'promptPreview',
    `프롬프트 미리보기: ${prompt.name}`,
    vscode.ViewColumn.Beside,
    {
      enableScripts: false,
      retainContextWhenHidden: true
    }
  );

  panel.webview.html = this.getPreviewHtml(prompt);
}

private getPreviewHtml(prompt: PromptTemplate): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>프롬프트 미리보기</title>
      <style>
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          line-height: 1.6;
          margin: 20px;
          color: var(--vscode-foreground);
          background-color: var(--vscode-editor-background);
        }
        .header {
          border-bottom: 1px solid var(--vscode-panel-border);
          padding-bottom: 10px;
          margin-bottom: 20px;
        }
        .title { font-size: 1.5em; font-weight: bold; }
        .description { color: var(--vscode-descriptionForeground); }
        .tags { margin-top: 10px; }
        .tag {
          display: inline-block;
          background: var(--vscode-badge-background);
          color: var(--vscode-badge-foreground);
          padding: 2px 8px;
          border-radius: 3px;
          margin-right: 5px;
          font-size: 0.8em;
        }
        .content {
          white-space: pre-wrap;
          font-family: 'Courier New', monospace;
          background: var(--vscode-textCodeBlock-background);
          padding: 15px;
          border-radius: 5px;
          border: 1px solid var(--vscode-panel-border);
        }
      </style>
    </head>
    <body>
      <div class="header">
        <div class="title">${prompt.name}</div>
        <div class="description">${prompt.description}</div>
        <div class="tags">
          ${prompt.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
        </div>
      </div>
      <div class="content">${this.escapeHtml(prompt.content)}</div>
    </body>
    </html>
  `;
}

private escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

private async openAsNewFile(prompt: PromptTemplate): Promise<void> {
  const doc = await vscode.workspace.openTextDocument({
    content: prompt.content,
    language: 'markdown'
  });
  
  await vscode.window.showTextDocument(doc);
}
```

### 5단계: 프롬프트 동기화 서비스
```typescript
// src/services/promptSyncService.ts
import { PromptLoader } from './promptLoader';
import { PromptPalette } from '../ui/promptPalette';
import { TeamConfig } from '../types/config';

export class PromptSyncService {
  private promptLoader: PromptLoader;
  private promptPalette: PromptPalette;

  constructor() {
    this.promptLoader = new PromptLoader();
    this.promptPalette = new PromptPalette();
  }

  async syncPrompts(configDir: string, teamConfig: TeamConfig): Promise<void> {
    try {
      const prompts = await this.promptLoader.loadPrompts(configDir, teamConfig);
      const categories = this.promptLoader.groupByCategory(prompts);
      
      // 프롬프트 데이터를 전역 상태에 저장 (확장 컨텍스트 활용)
      this.storePrompts(categories);
      
      vscode.window.showInformationMessage(`${prompts.length}개의 프롬프트를 로드했습니다`);
    } catch (error) {
      throw new Error(`프롬프트 동기화 실패: ${error}`);
    }
  }

  async showPromptPalette(): Promise<void> {
    const categories = this.getStoredPrompts();
    if (categories.length === 0) {
      vscode.window.showWarningMessage('로드된 프롬프트가 없습니다. 먼저 팀 설정을 동기화하세요.');
      return;
    }

    await this.promptPalette.showPromptPalette(categories);
  }

  private storePrompts(categories: any[]): void {
    // VS Code 확장 컨텍스트에 저장
    // 실제 구현에서는 ExtensionContext.globalState 사용
  }

  private getStoredPrompts(): any[] {
    // 저장된 프롬프트 데이터 반환
    return [];
  }
}
```

### 6단계: 명령어 등록 및 통합
```typescript
// src/extension.ts 업데이트
import { PromptSyncService } from './services/promptSyncService';

export function activate(context: vscode.ExtensionContext) {
    const promptSyncService = new PromptSyncService();

    // 프롬프트 팔레트 명령어
    const promptPaletteCommand = vscode.commands.registerCommand('teamsync.showPrompts', async () => {
        await promptSyncService.showPromptPalette();
    });

    // 기존 syncSettings 명령어 업데이트
    const syncCommand = vscode.commands.registerCommand('teamsync.syncSettings', async () => {
        try {
            const repoUrl = await vscode.window.showInputBox({
                prompt: '팀 설정 저장소 URL을 입력하세요'
            });

            if (repoUrl) {
                const syncService = new SyncService();
                const config = await syncService.syncTeamSettings(repoUrl);
                
                // 모든 동기화 실행
                const settingsSyncService = new SettingsSyncService();
                await settingsSyncService.syncVSCodeSettings('.teamsync', config);
                
                const extensionsSyncService = new ExtensionsSyncService();
                await extensionsSyncService.syncExtensions('.teamsync', config);
                
                // 프롬프트 동기화
                await promptSyncService.syncPrompts('.teamsync', config);
                
                vscode.window.showInformationMessage('팀 설정 동기화 완료!');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`동기화 실패: ${error}`);
        }
    });

    context.subscriptions.push(syncCommand, promptPaletteCommand);
}
```

## ✅ 완료 기준
- [ ] 프롬프트 로드 및 파싱 기능 구현
- [ ] QuickPick 기반 프롬프트 선택 UI 구현
- [ ] 프롬프트 미리보기 기능 구현
- [ ] 클립보드 복사 및 파일 열기 기능 구현

## 🔗 다음 단계
007-integration-testing.md - 기능 통합 및 테스트

## 📚 참고 자료
- [VS Code QuickPick API](https://code.visualstudio.com/api/references/vscode-api#QuickPick)
- [Webview API](https://code.visualstudio.com/api/extension-guides/webview)
