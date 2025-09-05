export interface TeamConfig {
  version: string;
  organization: {
    name: string;
    repository: string;
  };
  settings: {
    vscode: {
      settings?: string;
      keybindings?: string;
      extensions?: string;
    };
    code_quality?: {
      editorconfig?: string;
      prettier?: string;
      eslint?: string;
    };
  };
  prompts: PromptConfig[];
  policies: {
    sync_mode: 'recommended' | 'force';
    auto_update: boolean;
    backup_local: boolean;
  };
}

export interface PromptConfig {
  name: string;
  file: string;
  category: string;
}
