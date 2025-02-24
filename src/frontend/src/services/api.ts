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

export const apiService = {
  // Get all available voices
  getVoices: async (): Promise<Voice[]> => {
    const response = await api.get<Voice[]>('/voices');
    return response.data;
  },

  // Convert text to speech
  textToSpeech: async (text: string, voiceId: string): Promise<Blob> => {
    const response = await api.post(
      '/tts',
      { text, voice_id: voiceId },
      { responseType: 'blob' }
    );
    return response.data;
  },

  // Get audio stream URL
  getAudioUrl: (blob: Blob): string => {
    return URL.createObjectURL(blob);
  },
};

export default apiService; 