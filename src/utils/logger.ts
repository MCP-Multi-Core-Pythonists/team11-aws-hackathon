import * as vscode from 'vscode';

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

export class Logger {
  private static outputChannel: vscode.OutputChannel | undefined;

  static initialize(): void {
    if (!this.outputChannel) {
      this.outputChannel = vscode.window.createOutputChannel('TeamSync Pro');
    }
  }

  static log(level: LogLevel, message: string, error?: any): void {
    if (!this.outputChannel) {
      this.initialize();
    }

    const timestamp = new Date().toISOString();
    const levelStr = LogLevel[level];
    const logMessage = `[${timestamp}] ${levelStr}: ${message}`;

    this.outputChannel!.appendLine(logMessage);

    if (error) {
      this.outputChannel!.appendLine(`Error details: ${JSON.stringify(error, null, 2)}`);
    }

    if (level === LogLevel.ERROR) {
      vscode.window.showErrorMessage(`TeamSync Pro: ${message}`);
    }
  }

  static debug(message: string): void {
    this.log(LogLevel.DEBUG, message);
  }

  static info(message: string): void {
    this.log(LogLevel.INFO, message);
  }

  static warn(message: string): void {
    this.log(LogLevel.WARN, message);
  }

  static error(message: string, error?: any): void {
    this.log(LogLevel.ERROR, message, error);
  }

  static show(): void {
    if (!this.outputChannel) {
      this.initialize();
    }
    this.outputChannel!.show();
  }
}
