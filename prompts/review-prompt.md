# 코드 리뷰 프롬프트 (Code Review Prompt)

## 시니어/주니어 개발자별 리뷰 포인트

### 주니어 개발자 리뷰 시 중점사항
- **기본 원칙 준수**: 네이밍 컨벤션, 코드 포맷팅
- **로직 이해도**: 비즈니스 요구사항 반영 여부
- **에러 처리**: 기본적인 예외 상황 대응
- **테스트 작성**: 단위 테스트 포함 여부

### 시니어 개발자 리뷰 시 중점사항
- **아키텍처 설계**: 확장성과 유지보수성
- **성능 최적화**: 병목 지점 식별 및 개선
- **보안 고려사항**: 잠재적 취약점 검토
- **팀 표준 준수**: 코딩 가이드라인 및 베스트 프랙티스

## 기능별 리뷰 템플릿

### 1. 기능 추가 리뷰 템플릿
```markdown
## 기능 검토
- [ ] 요구사항 충족도 확인
- [ ] 기존 기능에 미치는 영향 분석
- [ ] 에지 케이스 처리 여부
- [ ] 성능 영향도 평가

## 코드 품질
- [ ] 함수/클래스 단일 책임 원칙 준수
- [ ] 적절한 추상화 레벨
- [ ] 코드 중복 최소화
- [ ] 네이밍의 명확성

## 테스트
- [ ] 단위 테스트 포함
- [ ] 통합 테스트 필요성 검토
- [ ] 테스트 커버리지 적절성
- [ ] 테스트 케이스의 완전성

## 보안
- [ ] 입력 검증 적절성
- [ ] 권한 검사 포함
- [ ] 민감 정보 노출 방지
- [ ] SQL 인젝션 등 취약점 검토
```

### 2. 버그 수정 리뷰 템플릿
```markdown
## 버그 분석
- [ ] 근본 원인 파악 및 해결
- [ ] 유사한 버그 발생 가능성 검토
- [ ] 수정 범위의 적절성
- [ ] 사이드 이펙트 가능성 분석

## 수정 방법
- [ ] 최소한의 변경으로 문제 해결
- [ ] 기존 로직에 미치는 영향 최소화
- [ ] 향후 유지보수 고려
- [ ] 임시 방편이 아닌 근본적 해결

## 검증
- [ ] 버그 재현 테스트 케이스 추가
- [ ] 회귀 테스트 실행
- [ ] 관련 기능 동작 확인
- [ ] 성능 영향도 측정
```

### 3. 리팩토링 리뷰 템플릿
```markdown
## 리팩토링 목적
- [ ] 개선 목표 명확성
- [ ] 비즈니스 가치 연결
- [ ] 기술 부채 해결 정도
- [ ] 향후 개발 효율성 향상

## 변경 범위
- [ ] 적절한 범위 설정
- [ ] 점진적 개선 계획
- [ ] 기존 기능 보존
- [ ] API 호환성 유지

## 품질 개선
- [ ] 코드 복잡도 감소
- [ ] 가독성 향상
- [ ] 테스트 용이성 개선
- [ ] 성능 최적화 효과
```

## 자동화된 리뷰 도구 연동

### 1. 정적 분석 도구 설정
```yaml
# .github/workflows/code-review.yml
name: Automated Code Review
on: [pull_request]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run ESLint
        run: npx eslint src/ --format json --output-file eslint-report.json
      - name: Run SonarQube
        run: sonar-scanner
      - name: Security Scan
        run: npm audit --audit-level moderate
```

### 2. 코드 커버리지 체크
```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx,ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

## 건설적인 피드백 템플릿

### 1. 개선 제안 방식
```markdown
## 현재 코드
```javascript
// 검토 대상 코드
function calculateTotal(items) {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    total += items[i].price * items[i].quantity;
  }
  return total;
}
```

## 개선 제안
```javascript
// 함수형 프로그래밍 스타일로 개선
const calculateTotal = (items) => 
  items.reduce((total, item) => total + (item.price * item.quantity), 0);
```

## 개선 이유
- 코드 간결성 향상
- 함수형 프로그래밍 패러다임 적용
- 불변성 보장
- 가독성 개선
```

### 2. 질문 형태의 피드백
```markdown
## 검토 의견
- 이 함수가 null 값을 받았을 때 어떻게 동작할까요?
- 성능상 더 효율적인 방법이 있을까요?
- 테스트 케이스에서 고려해야 할 엣지 케이스가 있을까요?
- 이 로직을 재사용 가능한 유틸리티로 분리하면 어떨까요?
```

## 리뷰 효율성 향상 프로세스

### 1. 리뷰 전 체크리스트 (작성자)
- [ ] 자체 코드 리뷰 완료
- [ ] 테스트 실행 및 통과 확인
- [ ] 린터 및 포맷터 실행
- [ ] 커밋 메시지 작성 규칙 준수
- [ ] PR 설명 작성 (변경 사항, 테스트 방법 등)

### 2. 리뷰 시간 최적화
```markdown
## 리뷰 우선순위
1. 보안 관련 변경사항 (즉시)
2. 핵심 비즈니스 로직 (24시간 내)
3. 버그 수정 (48시간 내)
4. 기능 개선 (72시간 내)
5. 리팩토링 (1주일 내)
```

### 3. 리뷰 분담 전략
```javascript
// CODEOWNERS 파일 예시
# 전역 소유자
* @senior-dev-team

# 프론트엔드
/src/components/ @frontend-team
/src/styles/ @frontend-team

# 백엔드
/src/api/ @backend-team
/src/database/ @backend-team

# 보안 관련
/src/auth/ @security-team
/src/encryption/ @security-team
```

## 코드 품질 지표 활용

### 1. 객관적 지표 측정
```javascript
// 복잡도 측정
const complexity = require('complexity-report');
const report = complexity.run(sourceCode, {
  logicalor: true,
  switchcase: true,
  forin: false,
  trycatch: true
});

// 중복 코드 검출
const jscpd = require('jscpd');
const duplicates = jscpd.detect(['src/'], {
  min: 5,
  format: ['javascript', 'typescript']
});
```

### 2. 품질 게이트 설정
```yaml
# sonar-project.properties
sonar.qualitygate.wait=true
sonar.coverage.exclusions=**/*.test.js,**/*.spec.js
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# 품질 기준
sonar.coverage.minimum=80
sonar.duplicated_lines_density.maximum=3
sonar.complexity.maximum=10
```

## 리뷰 결과 추적 및 개선

### 1. 리뷰 메트릭 수집
```javascript
// 리뷰 통계 수집
const reviewMetrics = {
  averageReviewTime: '2.5 hours',
  defectDetectionRate: '85%',
  reviewCoverageRate: '95%',
  reworkRate: '12%'
};
```

### 2. 지속적 개선
```markdown
## 월간 리뷰 회고
- 자주 발견되는 이슈 패턴 분석
- 리뷰 프로세스 개선점 도출
- 팀원별 리뷰 스킬 향상 계획
- 자동화 도구 도입 검토
```
