import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient, Team } from '../api/client';
import TeamManagement from '../components/TeamManagement';
import PromptEditor from '../components/PromptEditor';

const Dashboard: React.FC = () => {
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'teams' | 'prompts' | 'configs'>('overview');

  // Fetch notifications
  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => apiClient.getNotifications()
  });

  const tabs = [
    { id: 'overview', name: '개요', icon: '📊' },
    { id: 'teams', name: '팀 관리', icon: '👥' },
    { id: 'prompts', name: '프롬프트', icon: '💬' },
    { id: 'configs', name: '설정', icon: '⚙️' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              TeamSync Pro
            </h1>
            <p className="text-lg text-gray-600">
              팀 개발 환경 설정 동기화 및 협업 도구
            </p>
          </div>

          {/* Navigation Tabs */}
          <div className="border-b border-gray-200 mb-8">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="mt-8">
            {activeTab === 'overview' && (
              <div className="space-y-8">
                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="p-5">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                            <span className="text-white font-semibold">👥</span>
                          </div>
                        </div>
                        <div className="ml-5 w-0 flex-1">
                          <dl>
                            <dt className="text-sm font-medium text-gray-500 truncate">
                              활성 팀
                            </dt>
                            <dd className="text-lg font-medium text-gray-900">
                              {selectedTeam ? selectedTeam.name : '선택된 팀 없음'}
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
                            <span className="text-white font-semibold">🔔</span>
                          </div>
                        </div>
                        <div className="ml-5 w-0 flex-1">
                          <dl>
                            <dt className="text-sm font-medium text-gray-500 truncate">
                              읽지 않은 알림
                            </dt>
                            <dd className="text-lg font-medium text-gray-900">
                              {notifications?.filter(n => !n.read).length || 0}
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
                          <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                            <span className="text-white font-semibold">⚙️</span>
                          </div>
                        </div>
                        <div className="ml-5 w-0 flex-1">
                          <dl>
                            <dt className="text-sm font-medium text-gray-500 truncate">
                              동기화 상태
                            </dt>
                            <dd className="text-lg font-medium text-gray-900">
                              최신
                            </dd>
                          </dl>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Recent Notifications */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-xl font-semibold mb-4">최근 알림</h3>
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
            )}

            {activeTab === 'teams' && (
              <TeamManagement 
                selectedTeam={selectedTeam} 
                onTeamSelect={setSelectedTeam} 
              />
            )}

            {activeTab === 'prompts' && (
              <PromptEditor selectedTeam={selectedTeam} />
            )}

            {activeTab === 'configs' && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">설정 관리</h2>
                <p className="text-gray-500">설정 관리 기능이 곧 추가될 예정입니다.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
