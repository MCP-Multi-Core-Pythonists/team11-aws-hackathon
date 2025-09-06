# TeamSync Push API Implementation

## Overview
TeamSync Extension의 Push 기능은 4개의 Cursor 설정 파일을 개별적으로 서버에 업로드합니다.

## API Specification

### Endpoint
```
POST /settings
Authorization: Bearer <token>
Content-Type: application/json
```

### Request Body
```json
{
  "name": "settings.json",
  "value": "{\"editor.fontSize\": 14}",
  "is_public": false
}
```

## Implementation Details

### 1. 지원하는 설정 파일
- `settings.json` - VSCode/Cursor 메인 설정
- `argv.json` - 실행 인자 설정
- `mcp.json` - Model Context Protocol 설정
- `extensions.json` - 확장 프로그램 목록

### 2. Push 프로세스
1. 사용자가 `TeamSync: Push Settings` 명령 실행
2. Public/Private 선택 UI 표시
3. 로컬 설정 파일들을 임시 디렉토리에 복사
4. 각 설정 파일을 개별적으로 API 호출하여 업로드
5. 결과 메시지 표시

### 3. API 호출 순서
```
POST /settings (settings.json)
POST /settings (argv.json)  
POST /settings (mcp.json)
POST /settings (extensions.json)
```

## 효율성 분석

### 현재 구현 (4개 API 호출)
**장점:**
- 각 파일별 개별 처리 가능
- 부분 실패 시 어떤 파일이 실패했는지 명확
- 서버에서 파일별 권한 관리 가능

**단점:**
- 네트워크 오버헤드 (4번의 HTTP 요청)
- 전체 처리 시간 증가
- 부분 성공/실패 상황 처리 복잡

### 개선 방안

#### Option 1: 배치 API
```json
POST /settings/batch
{
  "is_public": false,
  "settings": [
    {"name": "settings.json", "value": "..."},
    {"name": "argv.json", "value": "..."},
    {"name": "mcp.json", "value": "..."},
    {"name": "extensions.json", "value": "..."}
  ]
}
```

#### Option 2: 압축 업로드
```json
POST /settings/upload
{
  "is_public": false,
  "data": "base64-encoded-zip-file"
}
```

## 권장사항
현재 4개 API 호출 방식은 초기 구현으로는 적절하나, 사용자 증가 시 배치 API로 개선 권장.

## Error Handling
- 인증 실패: "Not authenticated. Please login first."
- 개별 파일 업로드 실패: "Failed to upload {filename}: {error}"
- 네트워크 오류: API 상태 코드와 함께 상세 에러 메시지 제공
