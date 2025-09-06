# 배포 프롬프트 (Deployment Prompt)

## 배포 전략

### 1. Blue-Green 배포
```yaml
# Blue-Green 배포 전략
# 현재 운영 중인 환경(Blue)과 새 버전 환경(Green)을 동시에 운영

# Blue 환경 (현재 운영)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
  labels:
    app: myapp
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 3000

---
# Green 환경 (새 버전)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
  labels:
    app: myapp
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: myapp
        image: myapp:v1.1.0
        ports:
        - containerPort: 3000

---
# 서비스 (트래픽 라우팅)
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
    version: blue  # 트래픽을 blue 또는 green으로 전환
  ports:
  - port: 80
    targetPort: 3000
```

### 2. 카나리 배포 (Canary Deployment)
```yaml
# 카나리 배포 - 트래픽의 일부만 새 버전으로 라우팅
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp-rollout
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10    # 10% 트래픽을 새 버전으로
      - pause: {duration: 5m}
      - setWeight: 30    # 30% 트래픽을 새 버전으로
      - pause: {duration: 10m}
      - setWeight: 50    # 50% 트래픽을 새 버전으로
      - pause: {duration: 10m}
      - setWeight: 100   # 100% 트래픽을 새 버전으로
      canaryService: myapp-canary
      stableService: myapp-stable
      trafficRouting:
        istio:
          virtualService:
            name: myapp-vs
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.1.0
        ports:
        - containerPort: 3000
```

### 3. 롤링 업데이트 (Rolling Update)
```yaml
# 롤링 업데이트 - 점진적으로 파드를 교체
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1      # 동시에 중단될 수 있는 최대 파드 수
      maxSurge: 2           # 동시에 생성될 수 있는 추가 파드 수
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:v1.1.0
        ports:
        - containerPort: 3000
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## CI/CD 파이프라인

### 1. GitHub Actions 워크플로우
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run security audit
        run: npm audit --audit-level moderate
      
      - name: Run linting
        run: npm run lint
      
      - name: Check code coverage
        run: npm run test:coverage
        env:
          CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}
      
      - name: Build and push Docker image
        id: build
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Deploy to staging
        run: |
          sed -i 's|IMAGE_TAG|${{ needs.build.outputs.image-tag }}|g' k8s/staging/deployment.yml
          kubectl apply -f k8s/staging/
      
      - name: Wait for deployment
        run: |
          kubectl rollout status deployment/myapp-staging -n staging --timeout=300s
      
      - name: Run smoke tests
        run: |
          npm run test:smoke -- --baseUrl=https://staging.example.com

  deploy-production:
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
      
      - name: Deploy to production (Blue-Green)
        run: |
          # 현재 활성 환경 확인
          CURRENT=$(kubectl get service myapp-service -o jsonpath='{.spec.selector.version}')
          if [ "$CURRENT" = "blue" ]; then
            NEW="green"
          else
            NEW="blue"
          fi
          
          # 새 환경에 배포
          sed -i "s|IMAGE_TAG|${{ needs.build.outputs.image-tag }}|g" k8s/production/deployment-${NEW}.yml
          kubectl apply -f k8s/production/deployment-${NEW}.yml
          
          # 배포 완료 대기
          kubectl rollout status deployment/myapp-${NEW} -n production --timeout=600s
          
          # 헬스 체크
          kubectl wait --for=condition=ready pod -l app=myapp,version=${NEW} -n production --timeout=300s
          
          # 트래픽 전환
          kubectl patch service myapp-service -p '{"spec":{"selector":{"version":"'${NEW}'"}}}'
          
          # 이전 환경 정리 (5분 후)
          sleep 300
          kubectl scale deployment myapp-${CURRENT} --replicas=0 -n production

  notify:
    needs: [deploy-production]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 2. Docker 최적화
```dockerfile
# 멀티 스테이지 빌드를 활용한 최적화된 Dockerfile
# Stage 1: 빌드 환경
FROM node:18-alpine AS builder

WORKDIR /app

# 의존성 파일만 먼저 복사 (캐시 최적화)
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# Stage 2: 프로덕션 환경
FROM node:18-alpine AS production

# 보안을 위한 non-root 사용자 생성
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

WORKDIR /app

# 필요한 파일만 복사
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

# 헬스 체크 추가
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

USER nextjs

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### 3. Kubernetes 매니페스트
```yaml
# k8s/production/namespace.yml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp-production

---
# k8s/production/configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: myapp-production
data:
  NODE_ENV: "production"
  LOG_LEVEL: "info"
  API_TIMEOUT: "30000"

---
# k8s/production/secret.yml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
  namespace: myapp-production
type: Opaque
data:
  DB_PASSWORD: <base64-encoded-password>
  JWT_SECRET: <base64-encoded-secret>
  API_KEY: <base64-encoded-api-key>

---
# k8s/production/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
  namespace: myapp-production
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:IMAGE_TAG
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: NODE_ENV
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: DB_PASSWORD
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL

---
# k8s/production/service.yml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: myapp-production
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
  type: ClusterIP

---
# k8s/production/ingress.yml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: myapp-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - api.example.com
    secretName: myapp-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-service
            port:
              number: 80

---
# k8s/production/hpa.yml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
  namespace: myapp-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 환경별 설정 관리

### 1. 환경 변수 관리
```javascript
// config/index.js
const config = {
  development: {
    port: 3000,
    database: {
      url: process.env.DB_URL || 'mongodb://localhost:27017/myapp_dev',
      options: {
        useNewUrlParser: true,
        useUnifiedTopology: true
      }
    },
    redis: {
      url: process.env.REDIS_URL || 'redis://localhost:6379'
    },
    logging: {
      level: 'debug'
    },
    cors: {
      origin: ['http://localhost:3000', 'http://localhost:3001']
    }
  },

  staging: {
    port: process.env.PORT || 3000,
    database: {
      url: process.env.DB_URL,
      options: {
        useNewUrlParser: true,
        useUnifiedTopology: true,
        ssl: true
      }
    },
    redis: {
      url: process.env.REDIS_URL,
      options: {
        tls: {}
      }
    },
    logging: {
      level: 'info'
    },
    cors: {
      origin: ['https://staging.example.com']
    }
  },

  production: {
    port: process.env.PORT || 3000,
    database: {
      url: process.env.DB_URL,
      options: {
        useNewUrlParser: true,
        useUnifiedTopology: true,
        ssl: true,
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000
      }
    },
    redis: {
      url: process.env.REDIS_URL,
      options: {
        tls: {},
        maxRetriesPerRequest: 3,
        retryDelayOnFailover: 100
      }
    },
    logging: {
      level: 'warn'
    },
    cors: {
      origin: ['https://example.com', 'https://www.example.com']
    },
    security: {
      helmet: true,
      rateLimit: {
        windowMs: 15 * 60 * 1000, // 15분
        max: 100 // 최대 100 요청
      }
    }
  }
};

const env = process.env.NODE_ENV || 'development';
module.exports = config[env];
```

### 2. 시크릿 관리
```bash
# Kubernetes Secrets 생성
kubectl create secret generic myapp-secrets \
  --from-literal=DB_PASSWORD=supersecretpassword \
  --from-literal=JWT_SECRET=jwtsecretkey \
  --from-literal=API_KEY=apikey123 \
  -n myapp-production

# 파일에서 시크릿 생성
kubectl create secret generic myapp-tls \
  --from-file=tls.crt=./certs/tls.crt \
  --from-file=tls.key=./certs/tls.key \
  -n myapp-production

# 시크릿 확인
kubectl get secrets -n myapp-production
kubectl describe secret myapp-secrets -n myapp-production
```

## 모니터링 및 로깅

### 1. Prometheus 모니터링
```yaml
# k8s/monitoring/prometheus-config.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
    - job_name: 'myapp'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        args:
        - '--config.file=/etc/prometheus/prometheus.yml'
        - '--storage.tsdb.path=/prometheus'
        - '--web.console.libraries=/etc/prometheus/console_libraries'
        - '--web.console.templates=/etc/prometheus/consoles'
      volumes:
      - name: config
        configMap:
          name: prometheus-config
```

### 2. 애플리케이션 로깅
```javascript
// logger.js
const winston = require('winston');
const { ElasticsearchTransport } = require('winston-elasticsearch');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: 'myapp',
    version: process.env.APP_VERSION,
    environment: process.env.NODE_ENV
  },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ]
});

// 프로덕션 환경에서는 Elasticsearch로 로그 전송
if (process.env.NODE_ENV === 'production') {
  logger.add(new ElasticsearchTransport({
    level: 'info',
    clientOpts: {
      node: process.env.ELASTICSEARCH_URL
    },
    index: 'myapp-logs'
  }));
}

module.exports = logger;
```

## 배포 체크리스트

### 배포 전 준비
- [ ] 코드 리뷰 완료
- [ ] 모든 테스트 통과
- [ ] 보안 스캔 통과
- [ ] 성능 테스트 완료
- [ ] 데이터베이스 마이그레이션 준비
- [ ] 환경 변수 및 시크릿 설정 확인
- [ ] 롤백 계획 수립

### 배포 진행 중
- [ ] 배포 스크립트 실행
- [ ] 헬스 체크 통과 확인
- [ ] 로그 모니터링
- [ ] 성능 지표 확인
- [ ] 에러율 모니터링

### 배포 완료 후
- [ ] 기능 테스트 수행
- [ ] 모니터링 대시보드 확인
- [ ] 사용자 피드백 수집
- [ ] 배포 결과 문서화
- [ ] 팀원들에게 배포 완료 알림

### 문제 발생 시
- [ ] 즉시 롤백 실행
- [ ] 장애 원인 분석
- [ ] 인시던트 리포트 작성
- [ ] 재발 방지 대책 수립
- [ ] 프로세스 개선 계획 수립
