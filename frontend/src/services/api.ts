import axios from "axios";
import { ApiResponse, Source, Page } from "../types/index";

// Create axios instance with base URL and default headers
const api = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// Sources API
export const sourcesApi = {
  // Get all sources
  getSources: async (): Promise<ApiResponse<Source[]>> => {
    const response = await api.get<ApiResponse<Source[]>>("/sources");
    return response.data;
  },

  // Get a single source by ID
  getSource: async (id: string): Promise<ApiResponse<Source>> => {
    const response = await api.get<ApiResponse<Source>>(`/sources/${id}`);
    return response.data;
  },

  // Create a new source
  createSource: async (
    source: Omit<Source, "id" | "createdAt" | "updatedAt">
  ): Promise<ApiResponse<Source>> => {
    const response = await api.post<ApiResponse<Source>>("/sources", source);
    return response.data;
  },

  // Update an existing source
  updateSource: async (
    id: string,
    source: Partial<Source>
  ): Promise<ApiResponse<Source>> => {
    const response = await api.put<ApiResponse<Source>>(
      `/sources/${id}`,
      source
    );
    return response.data;
  },

  // Delete a source
  deleteSource: async (id: string): Promise<ApiResponse<void>> => {
    const response = await api.delete<ApiResponse<void>>(`/sources/${id}`);
    return response.data;
  },
};

// Pages API
export const pagesApi = {
  // Get all pages for a source
  getPages: async (sourceId: string): Promise<ApiResponse<Page[]>> => {
    const response = await api.get<ApiResponse<Page[]>>(
      `/sources/${sourceId}/pages`
    );
    return response.data;
  },

  // Get a single page by ID
  getPage: async (
    sourceId: string,
    pageId: string
  ): Promise<ApiResponse<Page>> => {
    const response = await api.get<ApiResponse<Page>>(
      `/sources/${sourceId}/pages/${pageId}`
    );
    return response.data;
  },

  // Create a new page
  createPage: async (
    sourceId: string,
    page: FormData
  ): Promise<ApiResponse<Page>> => {
    const response = await api.post<ApiResponse<Page>>(
      `/sources/${sourceId}/pages`,
      page,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  // Upload multiple pages
  uploadPages: async (
    sourceId: string,
    files: FormData
  ): Promise<ApiResponse<Page[]>> => {
    const response = await api.post<ApiResponse<Page[]>>(
      `/sources/${sourceId}/pages/upload`,
      files,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  // Update an existing page
  updatePage: async (
    sourceId: string,
    pageId: string,
    page: Partial<Page>
  ): Promise<ApiResponse<Page>> => {
    const response = await api.put<ApiResponse<Page>>(
      `/sources/${sourceId}/pages/${pageId}`,
      page
    );
    return response.data;
  },

  // Delete a page
  deletePage: async (
    sourceId: string,
    pageId: string
  ): Promise<ApiResponse<void>> => {
    const response = await api.delete<ApiResponse<void>>(
      `/sources/${sourceId}/pages/${pageId}`
    );
    return response.data;
  },
};

// Search API
export const searchApi = {
  // Search for content across all sources and pages
  search: async (
    query: string,
    limit: number = 10,
    vector: boolean = false
  ): Promise<ApiResponse<{ sources: Source[]; pages: Page[] }>> => {
    const response = await api.get<
      ApiResponse<{ sources: Source[]; pages: Page[] }>
    >(`/search?q=${encodeURIComponent(query)}&limit=${limit}&vector=${vector}`);
    return response.data;
  },
};

export default api;
