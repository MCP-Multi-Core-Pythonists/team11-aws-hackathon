import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient, Team, TeamConfig, Prompt, Notification } from '../api/client';

const Dashboard: React.FC = () => {
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);

  // Fetch teams
  const { data: teams, isLoading: teamsLoading } = useQuery({
    queryKey: ['teams'],
    queryFn: () => apiClient.getTeams()
  });

  // Fetch team configs when team is selected
  const { data: configs } = useQuery({
    queryKey: ['teamConfigs', selectedTeam?.id],
    queryFn: () => selectedTeam ? apiClient.getTeamConfigs(selectedTeam.id) : Promise.resolve([]),
    enabled: !!selectedTeam
  });

  // Fetch team prompts when team is selected
  const { data: prompts } = useQuery({
    queryKey: ['teamPrompts', selectedTeam?.id],
    queryFn: () => selectedTeam ? apiClient.getTeamPrompts(selectedTeam.id) : Promise.resolve([]),
    enabled: !!selectedTeam
  });

  // Fetch notifications
  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => apiClient.getNotifications()
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              TeamSync Pro
            </h1>
            <p className="text-lg text-gray-600">
              팀 개발 환경 설정 동기화 및 협업 도구
            </p>
          </div>

          {/* Team Selection */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">내 팀</h2>
            {teamsLoading ? (
              <div className="text-center">로딩 중...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {teams?.map((team) => (
                  <div
                    key={team.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedTeam?.id === team.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedTeam(team)}
                  >
                    <h3 className="font-semibold text-lg">{team.name}</h3>
                    <p className="text-gray-600 text-sm">{team.description}</p>
                    <span className={`inline-block px-2 py-1 text-xs rounded-full mt-2 ${
                      team.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {team.is_public ? '공개' : '비공개'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Team Details */}
          {selectedTeam && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Team Configs */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4">팀 설정</h3>
                {configs && configs.length > 0 ? (
                  <div className="space-y-3">
                    {configs.map((config) => (
                      <div key={config.id} className="border rounded p-3">
                        <h4 className="font-medium">{config.name}</h4>
                        <p className="text-sm text-gray-600">
                          {Object.keys(config.settings_json).length}개 설정
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(config.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">설정이 없습니다.</p>
                )}
              </div>

              {/* Team Prompts */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-4">팀 프롬프트</h3>
                {prompts && prompts.length > 0 ? (
                  <div className="space-y-3">
                    {prompts.map((prompt) => (
                      <div key={prompt.id} className="border rounded p-3">
                        <h4 className="font-medium">{prompt.name}</h4>
                        <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                          {prompt.category}
                        </span>
                        <p className="text-sm text-gray-600 mt-2 truncate">
                          {prompt.content}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(prompt.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">프롬프트가 없습니다.</p>
                )}
              </div>
            </div>
          )}

          {/* Notifications */}
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold mb-4">알림</h3>
            {notifications && notifications.length > 0 ? (
              <div className="space-y-3">
                {notifications.slice(0, 5).map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-3 rounded border-l-4 ${
                      notification.read
                        ? 'border-gray-300 bg-gray-50'
                        : 'border-blue-500 bg-blue-50'
                    }`}
                  >
                    <p className="text-sm">{notification.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">알림이 없습니다.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
                          설정 동기화
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-semibold">팀</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          팀 관리
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          협업 도구
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                        <span className="text-white font-semibold">⚙️</span>
                      </div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">
                          설정 관리
                        </dt>
                        <dd className="text-lg font-medium text-gray-900">
                          중앙 집중식
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8">
              <a 
                href="/device" 
                className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                디바이스 인증
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
