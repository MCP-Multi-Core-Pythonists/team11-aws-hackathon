# TeamSync VSCode Extension

Cursor 설정을 팀과 공유하는 VSCode Extension입니다.

## 기능

- **로그인**: TeamSync 계정으로 로그인
- **Push Settings**: 현재 Cursor 설정을 서버에 업로드
- **Pull Settings**: 서버에서 최신 설정을 다운로드하여 적용

## 설치 및 실행

```bash
npm install
npm run compile
```

F5를 눌러 Extension Development Host에서 테스트할 수 있습니다.

## 명령어

- `TeamSync: Login` - 로그인
- `TeamSync: Push Settings` - 설정 업로드
- `TeamSync: Pull Settings` - 설정 다운로드

## 지원하는 Cursor 설정 파일

- `settings.json` - 메인 설정
- `argv.json` - 실행 인자 설정  
- `mcp.json` - MCP 설정
- `extensions.json` - 확장 프로그램 목록
