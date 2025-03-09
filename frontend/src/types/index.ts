// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  success: boolean;
  message?: string;
}

// Source Types
export interface Source {
  id: string;
  name: string;
  description?: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
}

export interface SourceCreate {
  name: string;
  description?: string;
  userId: string;
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
