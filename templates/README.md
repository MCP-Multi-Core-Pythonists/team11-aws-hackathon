# TeamSync Pro 템플릿 라이브러리

이 디렉토리는 팀 개발 프로세스를 표준화하고 효율성을 높이기 위한 템플릿 모음입니다.

## 📁 템플릿 구조

### 📝 개발 프로세스 템플릿
- **[commit-template.md](./commit-template.md)** - 일관된 커밋 메시지 작성 가이드
- **[feature-template.md](./feature-template.md)** - 기능 개발 계획 및 추적 템플릿
- **[test-template.md](./test-template.md)** - 체계적인 테스트 계획 및 실행 템플릿

## 🎯 템플릿 활용 가이드

### 1. 커밋 메시지 템플릿 (commit-template.md)
```bash
# Git 커밋 템플릿 설정
git config commit.template .gitmessage

# 사용 예시
feat(auth): 소셜 로그인 기능 추가

- Google OAuth 2.0 연동
- 사용자 프로필 자동 생성
- JWT 토큰 발급 로직 구현

Closes #123
```

**주요 기능:**
- 표준화된 커밋 메시지 형식
- 자동화 도구 연동 (Commitizen, Commitlint)
- 팀별 커스터마이징 가이드
- 자동 검증 규칙

### 2. 기능 개발 템플릿 (feature-template.md)
```markdown
## 기능 명세서
- **기능명**: 위시리스트 관리
- **담당자**: 홍길동
- **우선순위**: High
- **예상 개발 기간**: 5일

## 사용자 스토리
As a 온라인 쇼핑몰 고객,
I want 상품을 위시리스트에 추가하고 관리할 수 있는 기능,
So that 나중에 구매하고 싶은 상품들을 쉽게 찾아볼 수 있다.
```

**주요 기능:**
- 사용자 스토리 매핑 도구 연동
- 기술적 부채 추적
- 의존성 관리
- 완료 기준 (Definition of Done)

### 3. 테스트 템플릿 (test-template.md)
```javascript
// 테스트 계획서 기반 구조화된 테스트
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', async () => {
      // Given - 테스트 데이터 준비
      // When - 테스트 실행
      // Then - 결과 검증
    });
  });
});
```

**주요 기능:**
- 테스트 자동화 도구 연동
- 커버리지 추적
- 성능 테스트 템플릿
- E2E 테스트 가이드

## 🔄 워크플로우 통합

### 개발 프로세스와의 연동
```
1. 기능 계획 → feature-template.md 작성
2. 개발 진행 → prompts/ 디렉토리 프롬프트 활용
3. 테스트 작성 → test-template.md 기반 테스트 계획
4. 커밋 작성 → commit-template.md 기반 메시지 작성
5. 코드 리뷰 → review-prompt.md 기반 리뷰 진행
```

### CI/CD 파이프라인 연동
```yaml
# .github/workflows/template-validation.yml
name: Template Validation

on: [push, pull_request]

jobs:
  validate-commits:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate commit messages
        run: npx commitlint --from=HEAD~1 --to=HEAD --verbose

  validate-features:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check feature template compliance
        run: |
          # 기능 템플릿 준수 여부 검사
          ./scripts/validate-feature-template.sh

  validate-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check test coverage
        run: |
          npm test -- --coverage
          # 커버리지 임계값 검사
```

## 📊 템플릿 효과성 측정

### 측정 지표
- **일관성**: 커밋 메시지 형식 준수율
- **완성도**: 기능 개발 템플릿 항목 완료율
- **품질**: 테스트 커버리지 및 통과율
- **효율성**: 개발 시간 단축 효과

### 개선 프로세스
```markdown
## 월간 템플릿 리뷰
1. **사용 통계 분석**: 각 템플릿 사용 빈도 및 효과
2. **피드백 수집**: 팀원들의 개선 제안
3. **템플릿 업데이트**: 실제 사용 경험 반영
4. **교육 및 공유**: 새로운 기능 및 개선사항 전파
```

## 🛠️ 자동화 도구 연동

### 1. Commitizen 설정
```bash
# 전역 설치
npm install -g commitizen cz-conventional-changelog

# 프로젝트별 설정
echo '{ "path": "cz-conventional-changelog" }' > ~/.czrc

# 사용
git cz
```

### 2. Husky 훅 설정
```json
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
      "prettier --write"
    ],
    "*.md": [
      "markdownlint --fix"
    ]
  }
}
```

### 3. 템플릿 검증 스크립트
```bash
#!/bin/bash
# scripts/validate-templates.sh

echo "템플릿 검증 시작..."

# 커밋 메시지 검증
if ! npx commitlint --from=HEAD~1 --to=HEAD; then
  echo "❌ 커밋 메시지가 템플릿을 준수하지 않습니다."
  exit 1
fi

# 기능 템플릿 검증
if [ -f "docs/features/*.md" ]; then
  for file in docs/features/*.md; do
    if ! grep -q "## 사용자 스토리" "$file"; then
      echo "❌ $file에 사용자 스토리가 누락되었습니다."
      exit 1
    fi
  done
fi

# 테스트 템플릿 검증
if ! npm run test:coverage; then
  echo "❌ 테스트 커버리지가 기준을 충족하지 않습니다."
  exit 1
fi

echo "✅ 모든 템플릿 검증이 완료되었습니다."
```

## 🎨 팀별 커스터마이징

### 프론트엔드 팀 특화
```markdown
## 추가 템플릿 항목
- **접근성 체크리스트**: WCAG 2.1 AA 준수
- **브라우저 호환성**: 지원 브라우저 명시
- **성능 예산**: 번들 크기, 로딩 시간 목표
- **디자인 시스템**: 컴포넌트 재사용성 고려
```

### 백엔드 팀 특화
```markdown
## 추가 템플릿 항목
- **API 설계**: RESTful 원칙 준수
- **데이터베이스 스키마**: 정규화 및 인덱스 전략
- **보안 체크리스트**: OWASP Top 10 기반
- **성능 목표**: 응답 시간, 처리량 기준
```

### DevOps 팀 특화
```markdown
## 추가 템플릿 항목
- **인프라 코드**: Terraform, CloudFormation
- **모니터링 설정**: 메트릭, 알림 규칙
- **배포 전략**: Blue-Green, Canary 배포
- **장애 대응**: 롤백 계획, 복구 절차
```

## 📚 학습 리소스

### 템플릿 작성 가이드
- **커밋 메시지**: [Conventional Commits](https://www.conventionalcommits.org/)
- **사용자 스토리**: [User Story Mapping](https://www.jpattonassociates.com/user-story-mapping/)
- **테스트 전략**: [Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)

### 도구 문서
- **Commitizen**: [GitHub Repository](https://github.com/commitizen/cz-cli)
- **Commitlint**: [Official Documentation](https://commitlint.js.org/)
- **Husky**: [GitHub Repository](https://github.com/typicode/husky)

## 🔗 관련 프롬프트 연동

### prompts/ 디렉토리와의 연계
```
commit-template.md ↔ system-prompt.md (코드 품질 기준)
feature-template.md ↔ tdd-prompt.md (테스트 우선 개발)
test-template.md ↔ debugging-prompt.md (문제 해결 방법)
```

### 사용 시나리오
```
1. 새 기능 개발
   → feature-template.md로 계획 수립
   → system-prompt.md로 개발 가이드라인 확인
   → test-template.md로 테스트 계획 수립

2. 버그 수정
   → debugging-prompt.md로 문제 분석
   → commit-template.md로 수정 내용 기록
   → test-template.md로 회귀 테스트 추가

3. 리팩토링
   → refactor-prompt.md로 개선 계획 수립
   → commit-template.md로 변경 내용 기록
   → performance-prompt.md로 성능 개선 확인
```

## 📞 지원 및 기여

### 문의 채널
- **Slack**: #teamsync-pro-templates
- **이메일**: templates@teamsync-pro.com
- **GitHub Issues**: 버그 리포트 및 기능 요청

### 기여 방법
1. **새 템플릿 제안**: 팀에서 필요한 새로운 템플릿
2. **기존 템플릿 개선**: 사용 경험 기반 개선 제안
3. **자동화 도구 연동**: 새로운 도구 통합 방안
4. **문서화 개선**: 사용법 및 예시 보완

---

**마지막 업데이트**: 2024-12-05  
**버전**: v2.0  
**관리자**: TeamSync Pro Development Team
