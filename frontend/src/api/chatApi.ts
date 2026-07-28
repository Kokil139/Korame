import { apiClient } from "./client";

export async function submitBusinessRequirement(payload: { requirement: string }) {
  // POST to backend RTE endpoint. The backend should return JSON
  // with either { messages: [...] } or { questions: [...] } or a text response.
  const resp = await apiClient.post("/api/rte", payload);
  return resp.data;
}


