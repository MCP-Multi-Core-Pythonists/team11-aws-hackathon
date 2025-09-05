### 1. 사용자 관리
- 회원가입/로그인
- 비밀번호 찾기
- 프로필 수정

### 2. 팀 관리  
- 팀 만들기/삭제
- 팀원 초대하기
- 팀원 역할 설정 (관리자/일반)

### 3. 설정 파일 저장
- VS Code 설정 파일 업로드
- 확장 목록 저장
- 팀별로 설정 관리

### 4. 프롬프트 관리
- 프롬프트 작성/수정/삭제
- 카테고리별 분류 (코드리뷰, 문서화 등)
- 팀 내 공유

### 5. Git 연동
- GitHub 저장소 연결
- 설정 파일 자동 동기화
- 변경사항 알림

## 🔧 기본 기능 (있으면 좋은 것들)

### 6. 알림
- 팀 초대 알림
- 설정 변경 알림
- 이메일/앱 내 알림

### 7. 검색
- 프롬프트 검색
- 설정 검색
- 팀/사용자 검색

### 8. 활동 기록
- 누가 언제 뭘 했는지 기록
- 설정 변경 이력
- 사용 통계

## 📱 API 목록 (간단하게)

### 사용자
- `POST /auth/login` - 로그인
- `POST /auth/register` - 회원가입
- `GET /users/me` - 내 정보
- `PUT /users/me` - 정보 수정

### 팀
- `GET /teams` - 내 팀 목록
- `POST /teams` - 팀 생성
- `POST /teams/{id}/invite` - 팀원 초대
- `DELETE /teams/{id}/members/{userId}` - 팀원 제거

### 설정
- `GET /teams/{id}/configs` - 팀 설정 목록
- `POST /teams/{id}/configs` - 설정 업로드
- `PUT /teams/{id}/configs/{configId}` - 설정 수정
- `DELETE /teams/{id}/configs/{configId}` - 설정 삭제

### 프롬프트
- `GET /teams/{id}/prompts` - 팀 프롬프트 목록
- `POST /teams/{id}/prompts` - 프롬프트 생성
- `PUT /teams/{id}/prompts/{promptId}` - 프롬프트 수정
- `DELETE /teams/{id}/prompts/{promptId}` - 프롬프트 삭제

## 🗄️ 데이터베이스 테이블

### users (사용자)
- id, email, password, name, created_at

### teams (팀)
- id, name, description, owner_id, created_at

### team_members (팀 멤버)
- team_id, user_id, role, joined_at

### configs (설정)
- id, team_id, name, settings_json, created_by, created_at

### prompts (프롬프트)
- id, team_id, name, content, category, created_by, created_at

### notifications (알림)
- id, user_id, type, message, read, created_at