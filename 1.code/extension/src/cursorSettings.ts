import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface CursorSettings {
  settings: any;
  argv: any;
  mcp: any;
  extensions: any;
}

export class CursorSettingsManager {
  private readonly settingsPaths = {
    settings: path.join(os.homedir(), 'Library/Application Support/Cursor/User/settings.json'),
    argv: path.join(os.homedir(), '.cursor/argv.json'),
    mcp: path.join(os.homedir(), '.cursor/mcp.json'),
    extensions: path.join(os.homedir(), '.cursor/extensions/extensions.json')
  };

  private readonly tmpDir = path.join(os.tmpdir(), 'teamsync-cursor');

  async copySettingsToTemp(): Promise<string> {
    // tmp 디렉토리 생성
    if (!fs.existsSync(this.tmpDir)) {
      fs.mkdirSync(this.tmpDir, { recursive: true });
    }

    const copiedFiles: string[] = [];

    for (const [key, sourcePath] of Object.entries(this.settingsPaths)) {
      try {
        if (fs.existsSync(sourcePath)) {
          const destPath = path.join(this.tmpDir, `${key}.json`);
          fs.copyFileSync(sourcePath, destPath);
          copiedFiles.push(destPath);
        }
      } catch (error) {
        console.warn(`Failed to copy ${key}: ${error}`);
      }
    }

    return this.tmpDir;
  }

  async readAllSettings(): Promise<CursorSettings> {
    const settings: CursorSettings = {
      settings: {},
      argv: {},
      mcp: {},
      extensions: {}
    };

    for (const [key, filePath] of Object.entries(this.settingsPaths)) {
      try {
        if (fs.existsSync(filePath)) {
          const content = fs.readFileSync(filePath, 'utf8');
          settings[key as keyof CursorSettings] = JSON.parse(content);
        }
      } catch (error) {
        console.warn(`Failed to read ${key}: ${error}`);
      }
    }

    return settings;
  }

  async writeSettings(settings: CursorSettings): Promise<void> {
    // 먼저 tmp 디렉토리에 파일들을 생성
    const tmpFiles = await this.createTempFiles(settings);
    
    // tmp 파일들을 실제 경로로 복사
    for (const [key, content] of Object.entries(settings)) {
      try {
        const filePath = this.settingsPaths[key as keyof typeof this.settingsPaths];
        if (filePath && content && Object.keys(content).length > 0) {
          // 디렉토리 생성
          const dir = path.dirname(filePath);
          if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
          }
          
          fs.writeFileSync(filePath, JSON.stringify(content, null, 2));
        }
      } catch (error) {
        console.error(`Failed to write ${key}: ${error}`);
      }
    }
  }

  private async createTempFiles(settings: CursorSettings): Promise<string[]> {
    // tmp 디렉토리 생성
    if (!fs.existsSync(this.tmpDir)) {
      fs.mkdirSync(this.tmpDir, { recursive: true });
    }

    const createdFiles: string[] = [];

    for (const [key, content] of Object.entries(settings)) {
      try {
        if (content && Object.keys(content).length > 0) {
          const tmpFilePath = path.join(this.tmpDir, `${key}.json`);
          fs.writeFileSync(tmpFilePath, JSON.stringify(content, null, 2));
          createdFiles.push(tmpFilePath);
        }
      } catch (error) {
        console.warn(`Failed to create temp file for ${key}: ${error}`);
      }
    }

    return createdFiles;
  }
}
