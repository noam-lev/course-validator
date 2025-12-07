export const APP_NAME = 'Course Validator';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.trim() || '/api';

export const USE_MOCK_API =
  import.meta.env.VITE_USE_MOCK_API?.trim()?.toLowerCase() === 'true';

