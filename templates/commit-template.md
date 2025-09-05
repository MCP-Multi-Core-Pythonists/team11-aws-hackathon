# 커밋 메시지 템플릿 (Commit Message Template)

## 기본 커밋 메시지 형식

```
<타입>(<범위>): <제목>

<본문>

<푸터>
```

### 타입 (Type)
- **feat**: 새로운 기능 추가
- **fix**: 버그 수정
- **docs**: 문서 변경
- **style**: 코드 포맷팅, 세미콜론 누락 등 (기능 변경 없음)
- **refactor**: 코드 리팩토링 (기능 변경 없음)
- **test**: 테스트 코드 추가/수정
- **chore**: 빌드 프로세스, 도구 설정 변경

### 범위 (Scope)
- **auth**: 인증 관련
- **api**: API 관련
- **ui**: 사용자 인터페이스
- **db**: 데이터베이스
- **config**: 설정 파일
- **deps**: 의존성

## 커밋 메시지 예시

### 기능 추가
```
feat(auth): 소셜 로그인 기능 추가

- Google OAuth 2.0 연동
- 사용자 프로필 자동 생성
- JWT 토큰 발급 로직 구현

Closes #123
```

### 버그 수정
```
fix(api): 사용자 목록 조회 시 페이지네이션 오류 수정

페이지 번호가 0일 때 발생하는 오프셋 계산 오류를 수정했습니다.
- 최소 페이지 번호를 1로 설정
- 오프셋 계산 로직 개선

Fixes #456
```

### 리팩토링
```
refactor(ui): 사용자 컴포넌트 구조 개선

- UserCard 컴포넌트를 더 작은 단위로 분리
- 재사용 가능한 Avatar 컴포넌트 추출
- PropTypes 추가로 타입 안정성 향상

No breaking changes
```

## 자동화 도구 연동

### 1. Commitizen 설정
```bash
# 설치
npm install -g commitizen
npm install -g cz-conventional-changelog

# 설정
echo '{ "path": "cz-conventional-changelog" }' > ~/.czrc

# 사용
git cz
```

### 2. Commitlint 설정
```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']
    ],
    'subject-max-length': [2, 'always', 50],
    'body-max-line-length': [2, 'always', 72]
  }
};
```

### 3. Husky 훅 설정
```json
// package.json
{
  "husky": {
    "hooks": {
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS",
      "pre-commit": "lint-staged"
    }
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write",
      "git add"
    ]
  }
}
```

## 팀별 커스터마이징

### 프론트엔드 팀
```
feat(ui): 사용자 대시보드 반응형 디자인 구현

- 모바일, 태블릿, 데스크톱 브레이크포인트 적용
- CSS Grid를 활용한 레이아웃 최적화
- 터치 인터페이스 지원 추가

Tested on: Chrome 91+, Safari 14+, Firefox 89+
```

### 백엔드 팀
```
feat(api): 사용자 검색 API 성능 최적화

- Elasticsearch 인덱스 추가
- 검색 쿼리 응답 시간 50% 개선 (평균 200ms → 100ms)
- 페이지네이션 및 정렬 기능 추가

Performance: 1000 RPS 처리 가능
```

### DevOps 팀
```
chore(ci): Docker 빌드 프로세스 최적화

- 멀티 스테이지 빌드로 이미지 크기 40% 감소
- 빌드 캐시 활용으로 CI 시간 30% 단축
- 보안 스캔 단계 추가

Build time: 15min → 10min
Image size: 500MB → 300MB
```

## 자동 검증 규칙

### 1. 제목 검증
```javascript
// 제목 길이 제한 (50자)
const titleMaxLength = 50;

// 제목 형식 검증
const titlePattern = /^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+/;

function validateCommitTitle(title) {
  if (title.length > titleMaxLength) {
    throw new Error(`제목은 ${titleMaxLength}자를 초과할 수 없습니다.`);
  }
  
  if (!titlePattern.test(title)) {
    throw new Error('제목 형식이 올바르지 않습니다.');
  }
}
```

### 2. 본문 검증
```javascript
// 본문 줄 길이 제한 (72자)
const bodyMaxLineLength = 72;

function validateCommitBody(body) {
  const lines = body.split('\n');
  
  lines.forEach((line, index) => {
    if (line.length > bodyMaxLineLength) {
      throw new Error(`본문 ${index + 1}번째 줄이 ${bodyMaxLineLength}자를 초과합니다.`);
    }
  });
}
```

## 커밋 메시지 생성 도구

### 1. CLI 도구
```bash
#!/bin/bash
# commit-helper.sh

echo "커밋 타입을 선택하세요:"
echo "1) feat - 새로운 기능"
echo "2) fix - 버그 수정"
echo "3) docs - 문서 변경"
echo "4) refactor - 리팩토링"
echo "5) test - 테스트 추가/수정"

read -p "선택 (1-5): " choice

case $choice in
  1) type="feat" ;;
  2) type="fix" ;;
  3) type="docs" ;;
  4) type="refactor" ;;
  5) type="test" ;;
  *) echo "잘못된 선택입니다."; exit 1 ;;
esac

read -p "범위 (선택사항): " scope
read -p "제목: " title
read -p "본문 (선택사항): " body

if [ -n "$scope" ]; then
  commit_msg="$type($scope): $title"
else
  commit_msg="$type: $title"
fi

if [ -n "$body" ]; then
  commit_msg="$commit_msg\n\n$body"
fi

echo -e "$commit_msg" | git commit -F -
```

### 2. VS Code 확장 연동
```json
// .vscode/settings.json
{
  "git.inputValidation": "always",
  "git.inputValidationLength": 50,
  "git.inputValidationSubjectLength": 50,
  "conventionalCommits.scopes": [
    "auth",
    "api",
    "ui",
    "db",
    "config",
    "deps"
  ]
}
```

## 커밋 히스토리 분석

### 1. 통계 수집
```bash
# 타입별 커밋 수 분석
git log --oneline --grep="^feat" | wc -l
git log --oneline --grep="^fix" | wc -l
git log --oneline --grep="^refactor" | wc -l

# 작성자별 커밋 수
git shortlog -sn

# 월별 커밋 수
git log --format="%ad" --date=format:"%Y-%m" | sort | uniq -c
```

### 2. 품질 지표
```javascript
// 커밋 메시지 품질 분석
function analyzeCommitQuality(commits) {
  const metrics = {
    totalCommits: commits.length,
    withType: 0,
    withScope: 0,
    withBody: 0,
    averageTitleLength: 0
  };

  commits.forEach(commit => {
    const lines = commit.message.split('\n');
    const title = lines[0];
    
    // 타입 포함 여부
    if (/^(feat|fix|docs|style|refactor|test|chore)/.test(title)) {
      metrics.withType++;
    }
    
    // 범위 포함 여부
    if (/\(.+\):/.test(title)) {
      metrics.withScope++;
    }
    
    // 본문 포함 여부
    if (lines.length > 2) {
      metrics.withBody++;
    }
    
    metrics.averageTitleLength += title.length;
  });

  metrics.averageTitleLength = Math.round(metrics.averageTitleLength / commits.length);
  
  return metrics;
}
```
