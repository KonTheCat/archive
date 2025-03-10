// API Response Types
export interface ApiResponse<T> {
  data: T;
  usage?: UsageInfo;
  success: boolean;
  message?: string;
}

// Background Task Types
export interface BackgroundTask {
  id: string;
  taskType: string;
  status: "pending" | "in_progress" | "completed" | "failed" | "cancelled";
  sourceId?: string;
  pageId?: string;
  scheduledAt: string;
  canCancel: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  success: boolean;
  message?: string;
}

// Chat Types
export interface Citation {
  source_id: string;
  source_name: string;
  page_id: string;
  page_title?: string;
  text_snippet: string;
  similarity: number;
}

export interface UsageInfo {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export interface ChatRequest {
  message: string;
  vector_search?: boolean;
  sources_limit?: number;
}

// Source Types
export interface Source {
  id: string;
  name: string;
  description?: string;
  userId: string;
  startDate?: string;
  endDate?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SourceCreate {
  name: string;
  description?: string;
  userId: string;
  startDate?: string;
  endDate?: string;
}

// Page Types
export interface Page {
  id: string;
  sourceId: string;
  imageUrl: string;
  extractedText: string;
  title?: string;
  date?: string;
  notes?: string;
  contentVector?: number[];
  createdAt: string;
  updatedAt: string;
}

export interface PageCreate {
  sourceId: string;
  file: File;
  title?: string;
  date?: string;
  notes?: string;
}
