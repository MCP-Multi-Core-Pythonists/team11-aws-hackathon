import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, Team, Prompt } from '../api/client';
import toast from 'react-hot-toast';

interface PromptEditorProps {
  selectedTeam: Team | null;
}

const PromptEditor: React.FC<PromptEditorProps> = ({ selectedTeam }) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [newPrompt, setNewPrompt] = useState({ name: '', content: '', category: '' });
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const queryClient = useQueryClient();

  // Fetch prompts
  const { data: prompts, isLoading: promptsLoading } = useQuery({
    queryKey: ['teamPrompts', selectedTeam?.id],
    queryFn: () => selectedTeam ? apiClient.getTeamPrompts(selectedTeam.id) : Promise.resolve([]),
    enabled: !!selectedTeam
  });

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['promptCategories'],
    queryFn: () => apiClient.getPromptCategories()
  });

  // Create prompt mutation
  const createPromptMutation = useMutation({
    mutationFn: (promptData: { name: string; content: string; category: string }) =>
      selectedTeam ? apiClient.createTeamPrompt(selectedTeam.id, promptData) : Promise.reject('No team selected'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teamPrompts', selectedTeam?.id] });
      setShowCreateForm(false);
      setNewPrompt({ name: '', content: '', category: '' });
      toast.success('프롬프트가 생성되었습니다!');
    },
    onError: (error) => {
      toast.error('프롬프트 생성에 실패했습니다.');
      console.error('Prompt creation failed:', error);
    }
  });

  // Update prompt mutation
  const updatePromptMutation = useMutation({
    mutationFn: (data: { promptId: string; promptData: { name: string; content: string; category: string } }) =>
      selectedTeam ? apiClient.updateTeamPrompt(selectedTeam.id, data.promptId, data.promptData) : Promise.reject('No team selected'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teamPrompts', selectedTeam?.id] });
      setEditingPrompt(null);
      toast.success('프롬프트가 수정되었습니다!');
    },
    onError: (error) => {
      toast.error('프롬프트 수정에 실패했습니다.');
      console.error('Prompt update failed:', error);
    }
  });

  // Delete prompt mutation
  const deletePromptMutation = useMutation({
    mutationFn: (promptId: string) =>
      selectedTeam ? apiClient.deleteTeamPrompt(selectedTeam.id, promptId) : Promise.reject('No team selected'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teamPrompts', selectedTeam?.id] });
      toast.success('프롬프트가 삭제되었습니다.');
    },
    onError: (error) => {
      toast.error('프롬프트 삭제에 실패했습니다.');
      console.error('Prompt deletion failed:', error);
    }
  });

  const handleCreatePrompt = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPrompt.name.trim() && newPrompt.content.trim() && newPrompt.category) {
      createPromptMutation.mutate(newPrompt);
    }
  };

  const handleUpdatePrompt = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingPrompt && editingPrompt.name.trim() && editingPrompt.content.trim() && editingPrompt.category) {
      updatePromptMutation.mutate({
        promptId: editingPrompt.id,
        promptData: {
          name: editingPrompt.name,
          content: editingPrompt.content,
          category: editingPrompt.category
        }
      });
    }
  };

  const handleDeletePrompt = (prompt: Prompt) => {
    if (window.confirm(`"${prompt.name}" 프롬프트를 삭제하시겠습니까?`)) {
      deletePromptMutation.mutate(prompt.id);
    }
  };

  const filteredPrompts = prompts?.filter(prompt => 
    selectedCategory === 'all' || prompt.category === selectedCategory
  ) || [];

  if (!selectedTeam) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center">
        <p className="text-gray-500">팀을 선택하여 프롬프트를 관리하세요.</p>
      </div>
    );
  }

  if (promptsLoading) {
    return <div className="flex justify-center p-8">로딩 중...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">프롬프트 관리 - {selectedTeam.name}</h2>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            프롬프트 생성
          </button>
        </div>

        {/* Category Filter */}
        <div className="flex space-x-2 mb-4">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`px-3 py-1 rounded text-sm ${
              selectedCategory === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            전체
          </button>
          {categories?.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.name)}
              className={`px-3 py-1 rounded text-sm ${
                selectedCategory === category.name ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>

        {/* Create Form */}
        {showCreateForm && (
          <div className="mb-6 p-4 border rounded-lg bg-gray-50">
            <form onSubmit={handleCreatePrompt} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">프롬프트 이름</label>
                <input
                  type="text"
                  value={newPrompt.name}
                  onChange={(e) => setNewPrompt({ ...newPrompt, name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="프롬프트 이름을 입력하세요"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">카테고리</label>
                <select
                  value={newPrompt.category}
                  onChange={(e) => setNewPrompt({ ...newPrompt, category: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  <option value="">카테고리 선택</option>
                  {categories?.map((category) => (
                    <option key={category.id} value={category.name}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">프롬프트 내용</label>
                <textarea
                  value={newPrompt.content}
                  onChange={(e) => setNewPrompt({ ...newPrompt, content: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="프롬프트 내용을 입력하세요"
                  rows={6}
                  required
                />
              </div>
              <div className="flex space-x-2">
                <button
                  type="submit"
                  disabled={createPromptMutation.isPending}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
                >
                  {createPromptMutation.isPending ? '생성 중...' : '생성'}
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
      </div>

      {/* Prompts List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredPrompts.map((prompt) => (
          <div key={prompt.id} className="bg-white rounded-lg shadow p-6">
            {editingPrompt?.id === prompt.id ? (
              // Edit Form
              <form onSubmit={handleUpdatePrompt} className="space-y-4">
                <input
                  type="text"
                  value={editingPrompt.name}
                  onChange={(e) => setEditingPrompt({ ...editingPrompt, name: e.target.value })}
                  className="w-full border rounded px-3 py-2 font-semibold"
                  required
                />
                <select
                  value={editingPrompt.category}
                  onChange={(e) => setEditingPrompt({ ...editingPrompt, category: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  required
                >
                  {categories?.map((category) => (
                    <option key={category.id} value={category.name}>
                      {category.name}
                    </option>
                  ))}
                </select>
                <textarea
                  value={editingPrompt.content}
                  onChange={(e) => setEditingPrompt({ ...editingPrompt, content: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  rows={6}
                  required
                />
                <div className="flex space-x-2">
                  <button
                    type="submit"
                    disabled={updatePromptMutation.isPending}
                    className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600 disabled:opacity-50"
                  >
                    {updatePromptMutation.isPending ? '저장 중...' : '저장'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingPrompt(null)}
                    className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
                  >
                    취소
                  </button>
                </div>
              </form>
            ) : (
              // Display Mode
              <>
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-semibold text-lg">{prompt.name}</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setEditingPrompt(prompt)}
                      className="text-blue-500 hover:text-blue-700 text-sm"
                    >
                      수정
                    </button>
                    <button
                      onClick={() => handleDeletePrompt(prompt)}
                      disabled={deletePromptMutation.isPending}
                      className="text-red-500 hover:text-red-700 text-sm disabled:opacity-50"
                    >
                      삭제
                    </button>
                  </div>
                </div>
                <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full mb-3">
                  {prompt.category}
                </span>
                <p className="text-gray-700 whitespace-pre-wrap mb-4">{prompt.content}</p>
                <div className="text-xs text-gray-500">
                  생성일: {new Date(prompt.created_at).toLocaleString()}
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      {filteredPrompts.length === 0 && (
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <p className="text-gray-500">
            {selectedCategory === 'all' ? '프롬프트가 없습니다.' : `"${selectedCategory}" 카테고리에 프롬프트가 없습니다.`}
          </p>
        </div>
      )}
    </div>
  );
};

export default PromptEditor;
