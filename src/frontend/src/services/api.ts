import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Voice {
  voice_id: string;
  name: string;
}

export interface Model {
  model_id: string;
  name: string;
  description?: string;
}

export interface Config {
  default_voice_id: string;
  default_model_id: string;
  settings: {
    auto_play: boolean;
  };
}

export const apiService = {
  // Get all available voices
  getVoices: async (): Promise<Voice[]> => {
    const response = await api.get<Voice[]>('/voices');
    return response.data;
  },

  // Convert text to speech
  textToSpeech: async (text: string, voiceId?: string, modelId?: string): Promise<void> => {
    await api.post('/tts', { text, voice_id: voiceId, model_id: modelId });
  },

  // Get audio stream URL
  getAudioUrl: (blob: Blob): string => {
    return URL.createObjectURL(blob);
  },

  // Get all available models
  getModels: async (): Promise<Model[]> => {
    try {
      const response = await api.get<Model[]>('/models');
      return response.data;
    } catch (error) {
      console.error('Error fetching models:', error);
      return [];
    }
  },

  // Get current configuration
  getConfig: async (): Promise<Config> => {
    const response = await api.get<Config>('/config');
    return response.data;
  },

  // Update configuration
  updateConfig: async (config: Partial<Config>): Promise<Config> => {
    const response = await api.post<Config>('/config', config);
    return response.data;
  },
};

/**
 * Connect to the WebSocket server for streaming audio
 */
export const connectWebSocket = (
  onMessage: (event: MessageEvent) => void,
  onOpen?: () => void,
  onClose?: () => void,
  onError?: (event: Event) => void
): WebSocket => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${wsProtocol}//${window.location.hostname}:9020/ws`;
  
  const ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    console.log('WebSocket connection established');
    if (onOpen) onOpen();
  };
  
  ws.onmessage = onMessage;
  
  ws.onclose = () => {
    console.log('WebSocket connection closed');
    if (onClose) onClose();
  };
  
  ws.onerror = (event) => {
    console.error('WebSocket error:', event);
    if (onError) onError(event);
  };
  
  return ws;
};

export default apiService; 