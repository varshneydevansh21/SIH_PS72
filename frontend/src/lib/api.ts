import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 5000,
});

export const getNowcast = async () => {
  const { data } = await api.get('/nowcast/');
  return data;
};

export const getAlerts = async () => {
  const { data } = await api.get('/alerts/active');
  return data;
};

export const getRadarRecent = async () => {
  const { data } = await api.get('/radar/latest');
  return data;
};

export const getLightningRecent = async () => {
  const { data } = await api.get('/lightning/recent');
  return data;
};

export const getHealth = async () => {
  const { data } = await api.get('/health');
  return data;
};

export const getMetrics = async () => {
  const { data } = await api.get('/metrics');
  return data;
};

export const getReplayEvents = async () => {
  const { data } = await api.get('/replay/events');
  return data;
};

export const getReplayEvent = async (eventId: string) => {
  const { data } = await api.get(`/replay/events/${eventId}`);
  return data;
};

export default api;
