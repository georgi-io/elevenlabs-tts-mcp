import { useState, useEffect } from 'react'
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  IconButton,
  CircularProgress,
  Divider,
  useTheme,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Snackbar
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  RecordVoiceOver as MicIcon,
  VolumeUp as VolumeIcon,
  Settings as SettingsIcon,
  Save as SaveIcon
} from '@mui/icons-material'
import apiService, { Voice, Model, Config } from './services/api'

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#6366f1', // Indigo color
    },
    secondary: {
      main: '#10b981', // Emerald color
    },
    background: {
      default: '#f3f4f6',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
})

// Tab panel component
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [text, setText] = useState('')
  const [voices, setVoices] = useState<Voice[]>([])
  const [models, setModels] = useState<Model[]>([])
  const [selectedVoice, setSelectedVoice] = useState('')
  const [selectedModel, setSelectedModel] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState('')
  const [tabValue, setTabValue] = useState(0)
  const [config, setConfig] = useState<Config | null>(null)
  const [autoPlay, setAutoPlay] = useState(true)
  const [saveAudio, setSaveAudio] = useState(true)
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState('')

  // Fetch available voices, models and config on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch voices
        const voicesData = await apiService.getVoices()
        setVoices(voicesData)
        
        // Fetch models
        const modelsData = await apiService.getModels()
        setModels(modelsData)
        
        // Fetch config
        const configData = await apiService.getConfig()
        setConfig(configData)
        
        // Set selected voice and model from config
        if (configData) {
          setSelectedVoice(configData.default_voice_id)
          setSelectedModel(configData.default_model_id)
          setAutoPlay(configData.settings.auto_play)
          setSaveAudio(configData.settings.save_audio)
        } else if (voicesData.length > 0) {
          setSelectedVoice(voicesData[0].voice_id)
        }
      } catch (err) {
        console.error('Error fetching data:', err)
        setError('Failed to load data. Please try again later.')
      }
    }

    fetchData()
  }, [])

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handleTextToSpeech = async () => {
    if (!text.trim()) {
      setError('Please enter some text to convert')
      return
    }

    setIsLoading(true)
    setError('')
    
    try {
      const audioBlob = await apiService.textToSpeech(text, selectedVoice, selectedModel)
      const url = apiService.getAudioUrl(audioBlob)
      
      setAudioUrl(url)
      playAudio(url)
    } catch (err) {
      console.error('Error converting text to speech:', err)
      setError('Failed to convert text to speech. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const playAudio = (url: string) => {
    const audio = new Audio(url)
    audio.onplay = () => setIsPlaying(true)
    audio.onended = () => setIsPlaying(false)
    audio.play()
  }

  const stopAudio = () => {
    const audioElements = document.querySelectorAll('audio')
    audioElements.forEach(audio => {
      audio.pause()
      audio.currentTime = 0
    })
    setIsPlaying(false)
  }

  const saveConfiguration = async () => {
    if (!config) return
    
    try {
      const updatedConfig = await apiService.updateConfig({
        default_voice_id: selectedVoice,
        default_model_id: selectedModel,
        settings: {
          auto_play: autoPlay,
          save_audio: saveAudio
        }
      })
      
      setConfig(updatedConfig)
      setSnackbarMessage('Configuration saved successfully')
      setSnackbarOpen(true)
    } catch (err) {
      console.error('Error saving configuration:', err)
      setError('Failed to save configuration. Please try again.')
    }
  }

  const handleSnackbarClose = () => {
    setSnackbarOpen(false)
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Box display="flex" alignItems="center" justifyContent="center" mb={3}>
            <MicIcon color="primary" sx={{ fontSize: 36, mr: 1.5 }} />
            <Typography variant="h4" component="h1" color="primary.main">
              ElevenLabs Text-to-Speech
            </Typography>
          </Box>
          
          <Divider sx={{ mb: 3 }} />
          
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="app tabs">
              <Tab label="Text to Speech" id="tab-0" aria-controls="tabpanel-0" />
              <Tab label="Configuration" id="tab-1" aria-controls="tabpanel-1" />
            </Tabs>
          </Box>
          
          <TabPanel value={tabValue} index={0}>
            <FormControl fullWidth margin="normal">
              <InputLabel id="voice-select-label">Select Voice</InputLabel>
              <Select
                labelId="voice-select-label"
                id="voice-select"
                value={selectedVoice}
                label="Select Voice"
                onChange={(e) => setSelectedVoice(e.target.value)}
              >
                {voices.map((voice) => (
                  <MenuItem key={voice.voice_id} value={voice.voice_id}>
                    {voice.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="model-select-label">Select Model</InputLabel>
              <Select
                labelId="model-select-label"
                id="model-select"
                value={selectedModel}
                label="Select Model"
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {models.map((model) => (
                  <MenuItem key={model.model_id} value={model.model_id}>
                    {model.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <TextField
              id="text-input"
              label="Text to Convert"
              multiline
              rows={5}
              fullWidth
              margin="normal"
              placeholder="Enter text to convert to speech..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              variant="outlined"
            />
            
            <Box display="flex" justifyContent="space-between" alignItems="center" mt={3}>
              <Button
                variant="contained"
                color="primary"
                size="large"
                startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <VolumeIcon />}
                onClick={handleTextToSpeech}
                disabled={isLoading || !text.trim()}
              >
                {isLoading ? 'Converting...' : 'Convert to Speech'}
              </Button>
              
              {audioUrl && (
                <Box>
                  <IconButton
                    color="primary"
                    size="large"
                    onClick={() => playAudio(audioUrl)}
                    disabled={isPlaying}
                    sx={{ mr: 1 }}
                  >
                    <PlayIcon />
                  </IconButton>
                  
                  {isPlaying && (
                    <IconButton
                      color="secondary"
                      size="large"
                      onClick={stopAudio}
                    >
                      <StopIcon />
                    </IconButton>
                  )}
                </Box>
              )}
            </Box>
            
            {audioUrl && (
              <Box mt={3} p={2} bgcolor="background.default" borderRadius={1}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Audio Preview
                </Typography>
                <audio controls src={audioUrl} style={{ width: '100%' }} />
              </Box>
            )}
          </TabPanel>
          
          <TabPanel value={tabValue} index={1}>
            <Typography variant="h6" gutterBottom>
              Default Settings
            </Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="default-voice-label">Default Voice</InputLabel>
              <Select
                labelId="default-voice-label"
                id="default-voice"
                value={selectedVoice}
                label="Default Voice"
                onChange={(e) => setSelectedVoice(e.target.value)}
              >
                {voices.map((voice) => (
                  <MenuItem key={voice.voice_id} value={voice.voice_id}>
                    {voice.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="default-model-label">Default Model</InputLabel>
              <Select
                labelId="default-model-label"
                id="default-model"
                value={selectedModel}
                label="Default Model"
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {models.map((model) => (
                  <MenuItem key={model.model_id} value={model.model_id}>
                    {model.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
              General Settings
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={autoPlay}
                  onChange={(e) => setAutoPlay(e.target.checked)}
                  color="primary"
                />
              }
              label="Auto-play audio after conversion"
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={saveAudio}
                  onChange={(e) => setSaveAudio(e.target.checked)}
                  color="primary"
                />
              }
              label="Save audio files locally"
            />
            
            <Box display="flex" justifyContent="flex-end" mt={4}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<SaveIcon />}
                onClick={saveConfiguration}
              >
                Save Configuration
              </Button>
            </Box>
          </TabPanel>
        </Paper>
      </Container>
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        message={snackbarMessage}
      />
    </ThemeProvider>
  )
}

export default App
