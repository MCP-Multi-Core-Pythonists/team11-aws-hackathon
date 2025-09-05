# TeamSync Pro 프롬프트 라이브러리

이 디렉토리는 팀 개발 환경에서 일관되고 효과적인 결과를 생성하기 위한 프롬프트 모음입니다.

## 📁 프롬프트 구조

### 🔧 핵심 개발 프롬프트
- **[system-prompt.md](./system-prompt.md)** - 시스템 프롬프트 및 코드 품질 기준
- **[refactor-prompt.md](./refactor-prompt.md)** - 리팩토링 가이드 및 전략
- **[frontend-refactor-prompt.md](./frontend-refactor-prompt.md)** - 프론트엔드 특화 리팩토링
- **[review-prompt.md](./review-prompt.md)** - 코드 리뷰 가이드라인
- **[tdd-prompt.md](./tdd-prompt.md)** - TDD 개발 방법론

### 🛠️ 전문 영역 프롬프트
- **[debugging-prompt.md](./debugging-prompt.md)** - 디버깅 방법론 및 도구
- **[performance-prompt.md](./performance-prompt.md)** - 성능 최적화 전략
- **[security-prompt.md](./security-prompt.md)** - 보안 가이드라인 (OWASP 기반)
- **[documentation-prompt.md](./documentation-prompt.md)** - 효과적인 문서화 방법
- **[deployment-prompt.md](./deployment-prompt.md)** - 배포 전략 및 CI/CD

## 🎯 사용 방법

### 1. 역할별 프롬프트 선택
```
주니어 개발자 → system-prompt.md + tdd-prompt.md
시니어 개발자 → refactor-prompt.md + performance-prompt.md + security-prompt.md
팀 리더 → review-prompt.md + documentation-prompt.md + deployment-prompt.md
```

### 2. 단계별 프롬프트 활용
```
개발 시작 → system-prompt.md
코드 작성 → tdd-prompt.md
코드 개선 → refactor-prompt.md
문제 해결 → debugging-prompt.md
성능 개선 → performance-prompt.md
보안 검토 → security-prompt.md
코드 리뷰 → review-prompt.md
문서 작성 → documentation-prompt.md
배포 준비 → deployment-prompt.md
```

### 3. 프로젝트 유형별 조합
```
웹 애플리케이션:
- system-prompt.md + frontend-refactor-prompt.md + security-prompt.md

API 서버:
- system-prompt.md + performance-prompt.md + security-prompt.md + deployment-prompt.md

라이브러리/패키지:
- system-prompt.md + tdd-prompt.md + documentation-prompt.md
```

## 📋 템플릿 활용

### [templates/](../templates/) 디렉토리 연동
- **commit-template.md** - 일관된 커밋 메시지 작성
- **feature-template.md** - 기능 개발 계획 및 추적
- **test-template.md** - 체계적인 테스트 작성

### 사용 예시
```bash
# 새 기능 개발 시
1. feature-template.md로 기능 계획 수립
2. system-prompt.md로 개발 가이드라인 확인
3. tdd-prompt.md로 테스트 우선 개발
4. commit-template.md로 커밋 메시지 작성
5. review-prompt.md로 코드 리뷰 진행
```

## 🔄 프롬프트 업데이트 이력

### v2.0 (2024-12-05)
- **추가**: debugging-prompt.md, performance-prompt.md, security-prompt.md
- **개선**: system-prompt.md에 OWASP Top 10 기반 보안 가이드라인 추가
- **개선**: refactor-prompt.md에 자동화 도구 활용법 추가
- **개선**: review-prompt.md에 시니어/주니어별 리뷰 포인트 추가

### v1.0 (2024-11-01)
- **초기 버전**: system-prompt.md, refactor-prompt.md, review-prompt.md, tdd-prompt.md

## 📊 프롬프트 효과성 측정

### 측정 지표
- **코드 품질**: 복잡도, 중복도, 테스트 커버리지
- **개발 속도**: 기능 완성 시간, 버그 수정 시간
- **팀 일관성**: 코딩 스타일 준수율, 리뷰 시간
- **지식 공유**: 문서화 완성도, 팀원 만족도

### 개선 프로세스
1. **월간 회고**: 프롬프트 사용 경험 공유
2. **지표 분석**: 객관적 데이터 기반 효과 측정
3. **피드백 수집**: 팀원들의 개선 제안 수렴
4. **프롬프트 업데이트**: 실제 사용 경험 반영

## 🎨 팀별 커스터마이징

### 프론트엔드 팀
```
주요 프롬프트: frontend-refactor-prompt.md + performance-prompt.md
추가 고려사항: 
- 접근성 가이드라인
- 브라우저 호환성
- 사용자 경험 최적화
```

### 백엔드 팀
```
주요 프롬프트: system-prompt.md + security-prompt.md + performance-prompt.md
추가 고려사항:
- 데이터베이스 최적화
- API 설계 원칙
- 확장성 고려사항
```

### DevOps 팀
```
주요 프롬프트: deployment-prompt.md + security-prompt.md + debugging-prompt.md
추가 고려사항:
- 인프라 자동화
- 모니터링 전략
- 장애 대응 절차
```

## 🔗 관련 리소스

### 외부 참고 자료
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Clean Code 원칙](https://clean-code-developer.com/)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)

### 도구 연동
- **ESLint**: 코드 품질 자동 검사
- **Prettier**: 코드 포맷팅 자동화
- **Husky**: Git 훅을 통한 자동 검증
- **SonarQube**: 코드 품질 분석
- **Jest**: 테스트 자동화

## 📞 지원 및 문의

### 프롬프트 관련 문의
- **Slack**: #teamsync-pro-support
- **이메일**: teamsync-support@company.com
- **이슈 트래킹**: GitHub Issues

### 기여 방법
1. 새로운 프롬프트 제안
2. 기존 프롬프트 개선 제안
3. 사용 경험 및 피드백 공유
4. 버그 리포트 및 수정 제안

---

**마지막 업데이트**: 2024-12-05  
**버전**: v2.0  
**관리자**: TeamSync Pro Development Team
