# Pull API 문서

## 개요
Pull API는 사용자가 TeamSync 서버에서 최신 Cursor 설정을 다운로드하여 로컬에 적용할 수 있게 해주는 기능입니다.

## API 엔드포인트
```
GET /settings
Authorization: Bearer <token>
Content-Type: application/json
```

## 서버 응답 형식
```json
{
  "settings": [
    {
      "id": "settings_123456",
      "name": "settings.json",
      "content": {
        "editor.fontSize": 14,
        "editor.tabSize": 2
      },
      "visibility": "private",
      "group_id": "group_789",
      "created_at": "2025-09-06T05:59:18.375Z",
      "updated_at": "2025-09-06T05:59:18.375Z",
      "version": 1
    },
    {
      "id": "argv_123456",
      "name": "argv.json",
      "content": {
        "enable-crash-reporter": false
      },
      "visibility": "private",
      "group_id": "group_789",
      "created_at": "2025-09-06T05:59:18.375Z",
      "updated_at": "2025-09-06T05:59:18.375Z",
      "version": 1
    }
  ]
}
```

## 구현 세부사항

### 1. API 서비스 (`apiService.ts`)
- `pullSettings()` 메서드가 `/settings` 엔드포인트로 GET 요청을 보냄
- 서버 응답을 `CursorSettings` 형식으로 변환
- 파일명을 적절한 설정 카테고리로 매핑:
  - `settings.json` → `cursorSettings.settings`
  - `argv.json` → `cursorSettings.argv`
  - `mcp.json` → `cursorSettings.mcp`
  - `extensions.json` → `cursorSettings.extensions`

### 2. 설정 관리자 (`cursorSettings.ts`)
- `writeSettings()` 메서드가 다운로드된 설정을 처리
- `/tmp/teamsync-cursor/`에 임시 파일 생성
- 설정을 적절한 Cursor 구성 경로로 복사:
  - `~/Library/Application Support/Cursor/User/settings.json`
  - `~/.cursor/argv.json`
  - `~/.cursor/mcp.json`
  - `~/.cursor/extensions/extensions.json`

### 3. 확장 프로그램 명령어 (`extension.ts`)
- `teamsync.pullSettings` 명령어가 pull 작업을 실행
- 사용자에게 성공/오류 메시지 표시
- 인증 요구사항 처리

## 사용법
1. 로그인이 되어있는지 확인 (`TeamSync: Login`)
2. `TeamSync: Pull Settings` 명령어 실행
3. 설정이 자동으로 다운로드되고 적용됨
4. 변경사항을 보려면 Cursor 재시작

## 오류 처리
- API 호출 전 인증 확인
- 누락되거나 잘못된 설정의 우아한 처리
- VS Code 알림을 통한 사용자 피드백
- 안전한 작업을 위한 임시 파일 생성

## 파일 매핑
| 서버 파일명 | 로컬 경로 | 설명 |
|-------------|-----------|------|
| `settings.json` | `~/Library/Application Support/Cursor/User/settings.json` | 메인 에디터 설정 |
| `argv.json` | `~/.cursor/argv.json` | 명령줄 인수 |
| `mcp.json` | `~/.cursor/mcp.json` | MCP 구성 |
| `extensions.json` | `~/.cursor/extensions/extensions.json` | 확장 프로그램 목록 |

## 작업 완료 사항
✅ Pull API 구현 완료
✅ 서버 응답 형식에 맞춘 데이터 변환
✅ 임시 파일 생성 및 적절한 경로로 복사
✅ 오류 처리 및 사용자 피드백
✅ TypeScript 컴파일 확인 완료
