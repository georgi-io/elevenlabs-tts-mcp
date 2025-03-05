import { useState, useEffect, useRef } from 'react'
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
  ThemeProvider,
  createTheme,
  CssBaseline,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Snackbar,
  keyframes,
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  RecordVoiceOver as MicIcon,
  VolumeUp as VolumeIcon,
  Save as SaveIcon,
  GraphicEq as WaveIcon,
} from '@mui/icons-material'
import apiService, { Voice, Model, Config, connectWebSocket } from './services/api'
import { TabContext, TabList, TabPanel } from '@mui/lab'

// Create wave animation keyframes
const waveAnimation = keyframes`
  0% { transform: scaleY(0.5); }
  50% { transform: scaleY(1); }
  100% { transform: scaleY(0.5); }
`

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

function App() {
  const [selectedTab, setSelectedTab] = useState<string>('0');
  const [text, setText] = useState('');
  const [voices, setVoices] = useState<Voice[]>([])
  const [models, setModels] = useState<Model[]>([])
  const [selectedVoice, setSelectedVoice] = useState<string>('')
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [audioUrl, setAudioUrl] = useState<string>('')
  const [isPlaying, setIsPlaying] = useState<boolean>(false)
  const [error, setError] = useState<string>('')
  const [config, setConfig] = useState<Config | null>(null)
  const [autoPlay, setAutoPlay] = useState(true)
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false)
  const [snackbarMessage, setSnackbarMessage] = useState<string>('')
  const wsRef = useRef<WebSocket | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const [isAudioInitialized, setIsAudioInitialized] = useState(false)

  // Update ensureAudioContext to set initialized state
  const ensureAudioContext = async () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext()
    }
    
    if (audioContextRef.current.state === 'suspended') {
      await audioContextRef.current.resume()
    }
    setIsAudioInitialized(true)
    return audioContextRef.current
  }

  // Update WebSocket message handler to remove debug logs
  useEffect(() => {
    const fetchData = async () => {
      try {
        const configData = await apiService.getConfig()
        setConfig(configData)
        
        const [voicesData, modelsData] = await Promise.all([
          apiService.getVoices(),
          apiService.getModels()
        ])
        
        setVoices(voicesData)
        setModels(modelsData)
        
        if (configData?.default_voice_id) {
          setSelectedVoice(configData.default_voice_id)
          setSelectedModel(configData.default_model_id || '')
          setAutoPlay(configData.settings.auto_play)
        } else if (voicesData.length > 0) {
          setSelectedVoice(voicesData[0].voice_id)
          if (modelsData.length > 0) {
            setSelectedModel(modelsData[0].model_id)
          }
        }

        if (!wsRef.current) {
          wsRef.current = connectWebSocket(
            async (event: MessageEvent) => {
              try {
                const message = JSON.parse(event.data)
                console.log('WebSocket message received:', message.type);
                
                switch (message.type) {
                  case 'audio_data':
                    try {
                      const audioContext = await ensureAudioContext()
                      const audioData = atob(message.data)
                      const arrayBuffer = new ArrayBuffer(audioData.length)
                      const view = new Uint8Array(arrayBuffer)
                      for (let i = 0; i < audioData.length; i++) {
                        view[i] = audioData.charCodeAt(i)
                      }
                      
                      audioContext.decodeAudioData(arrayBuffer, (buffer) => {
                        const source = audioContext.createBufferSource()
                        source.buffer = buffer
                        source.connect(audioContext.destination)
                        source.start(0)
                        setIsPlaying(true)
                        source.onended = () => {
                          setIsPlaying(false)
                        }
                      }, (err) => {
                        console.error('Error decoding audio data:', err)
                        setError('Error playing audio stream')
                      })
                    } catch (err) {
                      console.error('Error processing audio data:', err)
                      setError('Error initializing audio playback')
                    }
                    break
                    
                  case 'error':
                    console.error('WebSocket error message:', message.message)
                    setError(`Streaming error: ${message.message}`)
                    break

                  default:
                    console.log('Unknown message type:', message.type)
                }
              } catch (err) {
                console.error('Error processing WebSocket message:', err)
                setError('Error processing audio stream')
              }
            },
            () => {
              console.log('WebSocket opened')
              setError('')
            },
            () => {
              console.log('WebSocket closed')
              wsRef.current = null
            },
            () => {
              console.error('WebSocket connection error')
              setError('WebSocket connection error')
              wsRef.current = null
            }
          )
        }
      } catch (err) {
        console.error('Error in fetchData:', err)
        setError('Failed to load data. Please try again later.')
      }
    }

    fetchData()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [])

  const handleTabChange = (_event: React.SyntheticEvent, newValue: string) => {
    setSelectedTab(newValue)
  }

  const handleTextToSpeech = async () => {
    try {
      await ensureAudioContext();
      await apiService.textToSpeech(text);
    } catch (error) {
      console.error('Error in text to speech:', error);
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
          auto_play: autoPlay
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
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography variant="h4" align="center" sx={{ mb: 4, color: 'primary.main', fontWeight: 'bold' }}>
          Elevenlabs TTS Streamer
        </Typography>
        
        {!isAudioInitialized ? (
          <Box 
            sx={{ 
              width: '100%',
              mb: 3,
              p: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 1,
              borderRadius: 1,
              bgcolor: 'background.paper',
              border: '1px solid',
              borderColor: 'primary.main',
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'primary.main',
                color: 'white',
              },
              transition: 'all 0.3s ease',
            }}
            onClick={ensureAudioContext}
          >
            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
              Click to Initialize Audio
            </Typography>
          </Box>
        ) : (
          <Box 
            sx={{ 
              width: '100%',
              mb: 3,
              p: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 1,
              borderRadius: 1,
              bgcolor: 'primary.main',
              color: 'white',
            }}
          >
            <WaveIcon 
              sx={{
                animation: `${waveAnimation} 1.5s ease-in-out infinite`,
              }}
            />
            <Typography variant="h6" sx={{ fontWeight: 'medium' }}>
              Audio Ready
            </Typography>
          </Box>
        )}

        <Box sx={{ width: '100%', typography: 'body1' }}>
          <TabContext value={selectedTab}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <TabList onChange={(_event: React.SyntheticEvent, newValue: string) => setSelectedTab(newValue)} aria-label="lab API tabs example">
                <Tab label="Text to Speech" value="0" />
                <Tab label="Voice Configuration" value="1" />
              </TabList>
            </Box>
            
            <TabPanel value="0">
              <TextField
                id="text-input"
                label="Enter text to convert"
                multiline
                rows={4}
                value={text}
                onChange={(e) => setText(e.target.value)}
                fullWidth
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                onClick={handleTextToSpeech}
                disabled={!text.trim() || isLoading}
                fullWidth
              >
                {isLoading ? 'Converting...' : 'Convert to Speech'}
              </Button>
            </TabPanel>
            
            <TabPanel value="1">
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
          </TabContext>
        </Box>
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
