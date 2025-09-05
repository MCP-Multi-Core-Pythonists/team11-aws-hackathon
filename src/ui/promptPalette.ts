import * as vscode from 'vscode';
import { PromptTemplate, PromptCategory } from '../types/prompt';

export class PromptPalette {
  async showPromptPalette(categories: PromptCategory[]): Promise<void> {
    const selectedCategory = await this.selectCategory(categories);
    if (!selectedCategory) return;

    const selectedPrompt = await this.selectPrompt(selectedCategory.prompts);
    if (!selectedPrompt) return;

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
}
