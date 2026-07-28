import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  // Local LLM generations can be slow; match the backend Ollama provider's own timeout.
  timeout: 120_000,
});