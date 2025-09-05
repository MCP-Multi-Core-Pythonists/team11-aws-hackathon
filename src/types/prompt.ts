export interface PromptTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  content: string;
  tags: string[];
  author?: string;
  createdAt?: Date;
}

export interface PromptCategory {
  id: string;
  name: string;
  description: string;
  prompts: PromptTemplate[];
}
