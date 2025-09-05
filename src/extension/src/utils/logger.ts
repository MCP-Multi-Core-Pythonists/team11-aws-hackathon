import * as vscode from 'vscode';

export class Logger {
    private static outputChannel: vscode.OutputChannel;

    static initialize(): void {
        if (!this.outputChannel) {
            this.outputChannel = vscode.window.createOutputChannel('TeamSync Pro');
        }
    }

    static info(message: string, ...args: any[]): void {
        this.log('INFO', message, ...args);
    }

    static warn(message: string, ...args: any[]): void {
        this.log('WARN', message, ...args);
    }

    static error(message: string, ...args: any[]): void {
        this.log('ERROR', message, ...args);
    }

    static debug(message: string, ...args: any[]): void {
        this.log('DEBUG', message, ...args);
    }

    private static log(level: string, message: string, ...args: any[]): void {
        if (!this.outputChannel) {
            this.initialize();
        }

        const timestamp = new Date().toISOString();
        const formattedMessage = `[${timestamp}] [${level}] ${message}`;
        
        if (args.length > 0) {
            this.outputChannel.appendLine(`${formattedMessage} ${JSON.stringify(args)}`);
        } else {
            this.outputChannel.appendLine(formattedMessage);
        }

        // 개발 모드에서는 콘솔에도 출력
        if (process.env.NODE_ENV === 'development') {
            console.log(formattedMessage, ...args);
        }
    }

    static show(): void {
        if (this.outputChannel) {
            this.outputChannel.show();
        }
    }

    static dispose(): void {
        if (this.outputChannel) {
            this.outputChannel.dispose();
        }
    }
}
