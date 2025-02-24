import fs from 'fs';
import path from 'path';

interface Config {
  defaultVoiceId: string;
  stability: number;
  similarityBoost: number;
}

const CONFIG_FILE = path.join(process.cwd(), 'config.json');

const defaultConfig: Config = {
  defaultVoiceId: 'EXAVITQu4vr4xnSDxMaL',  // Example voice ID
  stability: 0.5,
  similarityBoost: 0.75
};

export function loadConfig(): Config {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const configData = fs.readFileSync(CONFIG_FILE, 'utf-8');
      return { ...defaultConfig, ...JSON.parse(configData) };
    }
  } catch (error) {
    console.error('Error loading config:', error);
  }
  return defaultConfig;
}

export function saveConfig(config: Partial<Config>): void {
  try {
    const currentConfig = loadConfig();
    const newConfig = { ...currentConfig, ...config };
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(newConfig, null, 2));
  } catch (error) {
    console.error('Error saving config:', error);
  }
}

export const config = loadConfig(); 