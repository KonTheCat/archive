import axios from "axios";
import {
  ApiResponse,
  Source,
  Page,
  ChatMessage,
  BackgroundTask,
} from "../types/index";

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
    try {
      // Log what we're sending for debugging
      console.log(
        `Uploading ${files.getAll("files").length} files to source ${sourceId}`
      );

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
    } catch (error: any) {
      console.error("Error uploading multiple pages:", error);
      if (error.response) {
        console.error("Response data:", error.response.data);
        console.error("Response status:", error.response.status);
        console.error("Response headers:", error.response.headers);
      }
      throw error;
    }
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
    vector: boolean = false,
    sourceIds: string[] = []
  ): Promise<ApiResponse<{ sources: Source[]; pages: Page[] }>> => {
    let url = `/search?q=${encodeURIComponent(
      query
    )}&limit=${limit}&vector=${vector}`;

    // Add source_ids parameter if provided
    if (sourceIds.length > 0) {
      url += `&source_ids=${sourceIds.join(",")}`;
    }

    const response = await api.get<
      ApiResponse<{ sources: Source[]; pages: Page[] }>
    >(url);
    return response.data;
  },
};

// Chat API
export const chatApi = {
  // Send a message to the chat API
  sendMessage: async (
    message: string,
    vectorSearch: boolean = true,
    sourcesLimit: number = 5,
    sourceIds: string[] = []
  ): Promise<ApiResponse<ChatMessage>> => {
    const response = await api.post<ApiResponse<ChatMessage>>("/chat", {
      message,
      vector_search: vectorSearch,
      sources_limit: sourcesLimit,
      source_ids: sourceIds.length > 0 ? sourceIds : undefined,
    });
    return response.data;
  },
};

// Tasks API
export const tasksApi = {
  // Get all tasks
  getTasks: async (): Promise<ApiResponse<BackgroundTask[]>> => {
    const response = await api.get<ApiResponse<BackgroundTask[]>>("/tasks");
    return response.data;
  },

  // Get a single task by ID
  getTask: async (id: string): Promise<ApiResponse<BackgroundTask>> => {
    const response = await api.get<ApiResponse<BackgroundTask>>(`/tasks/${id}`);
    return response.data;
  },

  // Cancel a task
  cancelTask: async (id: string): Promise<ApiResponse<BackgroundTask>> => {
    const response = await api.delete<ApiResponse<BackgroundTask>>(
      `/tasks/${id}`
    );
    return response.data;
  },

  // Cancel multiple tasks
  cancelTasks: async (
    taskIds: string[]
  ): Promise<ApiResponse<{ cancelled_count: number }>> => {
    const response = await api.delete<ApiResponse<{ cancelled_count: number }>>(
      "/tasks",
      {
        data: taskIds,
      }
    );
    return response.data;
  },

  // Cancel all tasks
  cancelAllTasks: async (): Promise<
    ApiResponse<{ cancelled_count: number }>
  > => {
    const response = await api.delete<ApiResponse<{ cancelled_count: number }>>(
      "/tasks"
    );
    return response.data;
  },
};

export default api;
