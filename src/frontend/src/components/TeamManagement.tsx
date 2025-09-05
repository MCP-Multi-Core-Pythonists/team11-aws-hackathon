import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, Team, TeamMember } from '../api/client';
import toast from 'react-hot-toast';

interface TeamManagementProps {
  selectedTeam: Team | null;
  onTeamSelect: (team: Team) => void;
}

const TeamManagement: React.FC<TeamManagementProps> = ({ selectedTeam, onTeamSelect }) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [newTeam, setNewTeam] = useState({ name: '', description: '', is_public: false });
  const [inviteEmail, setInviteEmail] = useState('');
  const queryClient = useQueryClient();

  // Fetch teams
  const { data: teams, isLoading: teamsLoading } = useQuery({
    queryKey: ['teams'],
    queryFn: () => apiClient.getTeams()
  });

  // Fetch team members when team is selected
  const { data: members } = useQuery({
    queryKey: ['teamMembers', selectedTeam?.id],
    queryFn: () => selectedTeam ? apiClient.getTeamMembers(selectedTeam.id) : Promise.resolve([]),
    enabled: !!selectedTeam
  });

  // Create team mutation
  const createTeamMutation = useMutation({
    mutationFn: (teamData: { name: string; description?: string; is_public: boolean }) =>
      apiClient.createTeam(teamData),
    onSuccess: (newTeam) => {
      queryClient.invalidateQueries({ queryKey: ['teams'] });
      setShowCreateForm(false);
      setNewTeam({ name: '', description: '', is_public: false });
      toast.success(`팀 "${newTeam.name}"이 생성되었습니다!`);
      onTeamSelect(newTeam);
    },
    onError: (error) => {
      toast.error('팀 생성에 실패했습니다.');
      console.error('Team creation failed:', error);
    }
  });

  // Invite member mutation
  const inviteMemberMutation = useMutation({
    mutationFn: (data: { teamId: string; email: string; role: string }) =>
      apiClient.inviteTeamMember(data.teamId, { email: data.email, role: data.role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teamMembers', selectedTeam?.id] });
      setShowInviteForm(false);
      setInviteEmail('');
      toast.success('팀원 초대가 완료되었습니다!');
    },
    onError: (error) => {
      toast.error('팀원 초대에 실패했습니다.');
      console.error('Member invitation failed:', error);
    }
  });

  // Remove member mutation
  const removeMemberMutation = useMutation({
    mutationFn: (data: { teamId: string; userId: string }) =>
      apiClient.removeTeamMember(data.teamId, data.userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teamMembers', selectedTeam?.id] });
      toast.success('팀원이 제거되었습니다.');
    },
    onError: (error) => {
      toast.error('팀원 제거에 실패했습니다.');
      console.error('Member removal failed:', error);
    }
  });

  const handleCreateTeam = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTeam.name.trim()) {
      createTeamMutation.mutate(newTeam);
    }
  };

  const handleInviteMember = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedTeam && inviteEmail.trim()) {
      inviteMemberMutation.mutate({
        teamId: selectedTeam.id,
        email: inviteEmail,
        role: 'member'
      });
    }
  };

  const handleRemoveMember = (member: TeamMember) => {
    if (selectedTeam && window.confirm(`${member.name}님을 팀에서 제거하시겠습니까?`)) {
      removeMemberMutation.mutate({
        teamId: selectedTeam.id,
        userId: member.user_id
      });
    }
  };

  if (teamsLoading) {
    return <div className="flex justify-center p-8">로딩 중...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Team List */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">내 팀</h2>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            팀 생성
          </button>
        </div>

        {/* Create Team Form */}
        {showCreateForm && (
          <div className="mb-6 p-4 border rounded-lg bg-gray-50">
            <form onSubmit={handleCreateTeam} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">팀 이름</label>
                <input
                  type="text"
                  value={newTeam.name}
                  onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="팀 이름을 입력하세요"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">설명</label>
                <textarea
                  value={newTeam.description}
                  onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="팀 설명을 입력하세요"
                  rows={3}
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_public"
                  checked={newTeam.is_public}
                  onChange={(e) => setNewTeam({ ...newTeam, is_public: e.target.checked })}
                  className="mr-2"
                />
                <label htmlFor="is_public" className="text-sm">공개 팀</label>
              </div>
              <div className="flex space-x-2">
                <button
                  type="submit"
                  disabled={createTeamMutation.isPending}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
                >
                  {createTeamMutation.isPending ? '생성 중...' : '생성'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                >
                  취소
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Teams Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {teams?.map((team) => (
            <div
              key={team.id}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedTeam?.id === team.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => onTeamSelect(team)}
            >
              <h3 className="font-semibold text-lg">{team.name}</h3>
              <p className="text-gray-600 text-sm mt-1">{team.description}</p>
              <div className="flex justify-between items-center mt-3">
                <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                  team.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {team.is_public ? '공개' : '비공개'}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(team.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Team Details */}
      {selectedTeam && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">팀 멤버 관리</h2>
            <button
              onClick={() => setShowInviteForm(true)}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              멤버 초대
            </button>
          </div>

          {/* Invite Form */}
          {showInviteForm && (
            <div className="mb-6 p-4 border rounded-lg bg-gray-50">
              <form onSubmit={handleInviteMember} className="flex space-x-4">
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="flex-1 border rounded px-3 py-2"
                  placeholder="초대할 이메일 주소"
                  required
                />
                <button
                  type="submit"
                  disabled={inviteMemberMutation.isPending}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
                >
                  {inviteMemberMutation.isPending ? '초대 중...' : '초대'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowInviteForm(false)}
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                >
                  취소
                </button>
              </form>
            </div>
          )}

          {/* Members List */}
          <div className="space-y-3">
            {members?.map((member) => (
              <div key={member.id} className="flex justify-between items-center p-3 border rounded">
                <div>
                  <h4 className="font-medium">{member.name}</h4>
                  <p className="text-sm text-gray-600">{member.email}</p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    member.role === 'owner' 
                      ? 'bg-purple-100 text-purple-800'
                      : member.role === 'admin'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {member.role === 'owner' ? '소유자' : member.role === 'admin' ? '관리자' : '멤버'}
                  </span>
                  {member.role !== 'owner' && (
                    <button
                      onClick={() => handleRemoveMember(member)}
                      disabled={removeMemberMutation.isPending}
                      className="text-red-500 hover:text-red-700 text-sm disabled:opacity-50"
                    >
                      제거
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamManagement;
