# Frontend Service 구현 명세서

## 1. 서비스 개요

### 1.1 목적
TeamSync Pro의 웹 콘솔로, 팀 관리, 설정 관리, 사용자 대시보드를 제공합니다.

### 1.2 기술 스택
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query + Context API
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **UI Components**: Headless UI + Custom Components

## 2. 아키텍처 설계

### 2.1 디렉토리 구조
```
src/frontend/
├── src/
│   ├── components/     # 재사용 가능한 컴포넌트
│   ├── pages/         # 페이지 컴포넌트
│   ├── hooks/         # 커스텀 훅
│   ├── services/      # API 서비스
│   ├── store/         # 상태 관리
│   ├── types/         # TypeScript 타입 정의
│   ├── utils/         # 유틸리티 함수
│   └── styles/        # 스타일 파일
├── public/
├── package.json
└── vite.config.ts
```

### 2.2 핵심 컴포넌트

#### 2.2.1 인증 시스템 (Authentication)
- **Device 인증**: VS Code Extension Device Flow 처리
- **OAuth 로그인**: Google, GitHub 소셜 로그인
- **토큰 관리**: JWT 토큰 자동 갱신

#### 2.2.2 대시보드 (Dashboard)
- **팀 개요**: 팀 목록, 멤버 현황, 활동 통계
- **설정 관리**: 팀 설정 조회/수정
- **사용자 프로필**: 개인 설정 관리

#### 2.2.3 팀 관리 (Team Management)
- **팀 생성/수정**: 팀 정보 관리
- **멤버 관리**: 초대, 권한 변경, 제거
- **설정 동기화**: 팀 설정 히스토리 조회

## 3. 페이지 구조

### 3.1 라우팅 구조
```typescript
const routes = [
  {
    path: '/',
    element: <Dashboard />,
    protected: true
  },
  {
    path: '/device',
    element: <DevicePage />,
    protected: false
  },
  {
    path: '/teams',
    element: <TeamsPage />,
    protected: true
  },
  {
    path: '/teams/:id',
    element: <TeamDetailPage />,
    protected: true
  },
  {
    path: '/settings',
    element: <SettingsPage />,
    protected: true
  }
];
```

### 3.2 주요 페이지

#### 3.2.1 Device 인증 페이지 (/device)
```typescript
interface DevicePageProps {
  userCode?: string; // URL 파라미터에서 추출
}

// 기능:
// - VS Code Extension에서 전달받은 코드 입력
// - 사용자 인증 처리
// - 인증 완료 후 Extension으로 토큰 전달
```

#### 3.2.2 대시보드 (/dashboard)
```typescript
interface DashboardData {
  user: User;
  teams: Team[];
  recentActivities: Activity[];
  statistics: {
    totalTeams: number;
    totalMembers: number;
    syncCount: number;
  };
}

// 기능:
// - 사용자 개요 정보 표시
// - 팀 목록 및 최근 활동
// - 빠른 액션 버튼
```

#### 3.2.3 팀 관리 페이지 (/teams)
```typescript
interface TeamsPageData {
  teams: Team[];
  invitations: Invitation[];
}

// 기능:
// - 팀 목록 조회/검색/필터링
// - 새 팀 생성
// - 팀 초대 관리
```

## 4. 컴포넌트 설계

### 4.1 공통 컴포넌트

#### 4.1.1 Layout Components
```typescript
// Header.tsx - 상단 네비게이션
interface HeaderProps {
  user?: User;
  onLogout: () => void;
}

// Sidebar.tsx - 사이드바 메뉴
interface SidebarProps {
  currentPath: string;
  teams: Team[];
}

// Layout.tsx - 전체 레이아웃
interface LayoutProps {
  children: React.ReactNode;
  sidebar?: boolean;
}
```

#### 4.1.2 UI Components
```typescript
// Button.tsx - 버튼 컴포넌트
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

// Modal.tsx - 모달 컴포넌트
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

// Table.tsx - 테이블 컴포넌트
interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pagination?: PaginationProps;
}
```

### 4.2 비즈니스 컴포넌트

#### 4.2.1 Team Components
```typescript
// TeamCard.tsx - 팀 카드
interface TeamCardProps {
  team: Team;
  onSelect: (team: Team) => void;
  onEdit: (team: Team) => void;
}

// TeamMemberList.tsx - 팀 멤버 목록
interface TeamMemberListProps {
  members: TeamMember[];
  currentUserId: string;
  onInvite: () => void;
  onRemove: (memberId: string) => void;
}

// TeamSettings.tsx - 팀 설정
interface TeamSettingsProps {
  team: Team;
  onUpdate: (settings: TeamSettings) => void;
}
```

#### 4.2.2 Configuration Components
```typescript
// ConfigurationViewer.tsx - 설정 뷰어
interface ConfigurationViewerProps {
  configuration: Configuration;
  readonly?: boolean;
}

// ConfigurationHistory.tsx - 설정 히스토리
interface ConfigurationHistoryProps {
  teamId: string;
  onRestore: (configId: string) => void;
}
```

## 5. 상태 관리

### 5.1 React Query 설정
```typescript
// queryClient.ts
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5분
    },
    mutations: {
      retry: 1,
    },
  },
});

// Query Keys
export const queryKeys = {
  user: ['user'] as const,
  teams: ['teams'] as const,
  team: (id: string) => ['team', id] as const,
  configurations: (teamId: string) => ['configurations', teamId] as const,
};
```

### 5.2 커스텀 훅

#### 5.2.1 인증 관련 훅
```typescript
// useAuth.ts
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const login = async (token: string) => {
    // 토큰 저장 및 사용자 정보 조회
  };

  const logout = () => {
    // 토큰 제거 및 상태 초기화
  };

  return { user, isLoading, login, logout };
}

// useDeviceAuth.ts
export function useDeviceAuth() {
  const approveDevice = useMutation({
    mutationFn: (userCode: string) => 
      authService.approveDevice(userCode),
    onSuccess: () => {
      toast.success('디바이스 인증이 완료되었습니다!');
    },
  });

  return { approveDevice };
}
```

#### 5.2.2 팀 관련 훅
```typescript
// useTeams.ts
export function useTeams() {
  return useQuery({
    queryKey: queryKeys.teams,
    queryFn: teamService.getTeams,
  });
}

// useTeam.ts
export function useTeam(teamId: string) {
  return useQuery({
    queryKey: queryKeys.team(teamId),
    queryFn: () => teamService.getTeam(teamId),
    enabled: !!teamId,
  });
}

// useCreateTeam.ts
export function useCreateTeam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: teamService.createTeam,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.teams });
      toast.success('팀이 생성되었습니다!');
    },
  });
}
```

## 6. API 서비스

### 6.1 HTTP 클라이언트 설정
```typescript
// api.ts
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
});

// 요청 인터셉터 - 토큰 자동 추가
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터 - 토큰 갱신
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 토큰 갱신 로직
      await refreshToken();
      return api.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

### 6.2 서비스 클래스

#### 6.2.1 인증 서비스
```typescript
// authService.ts
class AuthService {
  async approveDevice(userCode: string): Promise<void> {
    await api.post('/auth/device/approve', { user_code: userCode });
  }

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  }

  async refreshToken(): Promise<TokenResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  }
}

export const authService = new AuthService();
```

#### 6.2.2 팀 서비스
```typescript
// teamService.ts
class TeamService {
  async getTeams(): Promise<Team[]> {
    const response = await api.get('/teams');
    return response.data;
  }

  async getTeam(id: string): Promise<Team> {
    const response = await api.get(`/teams/${id}`);
    return response.data;
  }

  async createTeam(data: CreateTeamRequest): Promise<Team> {
    const response = await api.post('/teams', data);
    return response.data;
  }

  async updateTeam(id: string, data: UpdateTeamRequest): Promise<Team> {
    const response = await api.put(`/teams/${id}`, data);
    return response.data;
  }
}

export const teamService = new TeamService();
```

## 7. 스타일링 및 UI

### 7.1 Tailwind CSS 설정
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

### 7.2 컴포넌트 스타일 가이드
```typescript
// 색상 시스템
const colors = {
  primary: 'bg-blue-600 hover:bg-blue-700',
  secondary: 'bg-gray-600 hover:bg-gray-700',
  success: 'bg-green-600 hover:bg-green-700',
  danger: 'bg-red-600 hover:bg-red-700',
};

// 크기 시스템
const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

// 그림자 시스템
const shadows = {
  card: 'shadow-lg',
  modal: 'shadow-2xl',
  dropdown: 'shadow-xl',
};
```

## 8. 성능 최적화

### 8.1 코드 분할
```typescript
// 라우트 기반 코드 분할
const Dashboard = lazy(() => import('./pages/Dashboard'));
const TeamsPage = lazy(() => import('./pages/TeamsPage'));
const TeamDetailPage = lazy(() => import('./pages/TeamDetailPage'));

// 컴포넌트 기반 코드 분할
const HeavyComponent = lazy(() => import('./components/HeavyComponent'));
```

### 8.2 메모이제이션
```typescript
// React.memo 사용
export const TeamCard = React.memo<TeamCardProps>(({ team, onSelect }) => {
  return (
    <div onClick={() => onSelect(team)}>
      {/* 컴포넌트 내용 */}
    </div>
  );
});

// useMemo 사용
const filteredTeams = useMemo(() => {
  return teams.filter(team => 
    team.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
}, [teams, searchTerm]);

// useCallback 사용
const handleTeamSelect = useCallback((team: Team) => {
  navigate(`/teams/${team.id}`);
}, [navigate]);
```

### 8.3 이미지 최적화
```typescript
// 이미지 지연 로딩
const LazyImage: React.FC<{ src: string; alt: string }> = ({ src, alt }) => {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      className="w-full h-auto"
    />
  );
};

// 아바타 컴포넌트
const Avatar: React.FC<{ user: User; size?: 'sm' | 'md' | 'lg' }> = ({
  user,
  size = 'md'
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  return (
    <div className={`${sizeClasses[size]} rounded-full overflow-hidden`}>
      {user.avatar ? (
        <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
      ) : (
        <div className="w-full h-full bg-gray-300 flex items-center justify-center">
          {user.name.charAt(0).toUpperCase()}
        </div>
      )}
    </div>
  );
};
```

## 9. 테스트 전략

### 9.1 단위 테스트
```typescript
// Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### 9.2 통합 테스트
```typescript
// DevicePage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DevicePage } from './DevicePage';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe('DevicePage', () => {
  it('approves device with valid code', async () => {
    const queryClient = createTestQueryClient();
    
    render(
      <QueryClientProvider client={queryClient}>
        <DevicePage />
      </QueryClientProvider>
    );

    // 테스트 로직
  });
});
```

## 10. 배포 및 운영

### 10.1 빌드 설정
```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query'],
        },
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
});
```

### 10.2 환경 변수
```env
# .env.development
VITE_API_BASE_URL=http://localhost:3001/api/v1
VITE_APP_NAME=TeamSync Pro
VITE_APP_VERSION=1.0.0

# .env.production
VITE_API_BASE_URL=https://api.teamsync.pro/api/v1
VITE_APP_NAME=TeamSync Pro
VITE_APP_VERSION=1.0.0
```

## 11. TODO 및 향후 계획

### 11.1 단기 목표 (1주)
- [ ] 팀 설정 페이지 완성
- [ ] 실시간 알림 시스템
- [ ] 다크 모드 지원
- [ ] 모바일 반응형 개선

### 11.2 중기 목표 (1개월)
- [ ] 설정 비교 및 병합 UI
- [ ] 팀 템플릿 관리
- [ ] 사용 통계 대시보드
- [ ] 다국어 지원 (i18n)

### 11.3 장기 목표 (3개월)
- [ ] PWA 지원
- [ ] 오프라인 모드
- [ ] 고급 검색 및 필터링
- [ ] 사용자 커스터마이징
