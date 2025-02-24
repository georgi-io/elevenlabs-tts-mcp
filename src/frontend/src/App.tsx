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
  CssBaseline
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  RecordVoiceOver as MicIcon,
  VolumeUp as VolumeIcon
} from '@mui/icons-material'
import apiService, { Voice } from './services/api'

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
  const [text, setText] = useState('')
  const [voices, setVoices] = useState<Voice[]>([])
  const [selectedVoice, setSelectedVoice] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState('')

  // Fetch available voices on component mount
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const voicesData = await apiService.getVoices()
        setVoices(voicesData)
        if (voicesData.length > 0) {
          setSelectedVoice(voicesData[0].voice_id)
        }
      } catch (err) {
        console.error('Error fetching voices:', err)
        setError('Failed to load voices. Please try again later.')
      }
    }

    fetchVoices()
  }, [])

  const handleTextToSpeech = async () => {
    if (!text.trim()) {
      setError('Please enter some text to convert')
      return
    }

    setIsLoading(true)
    setError('')
    
    try {
      const audioBlob = await apiService.textToSpeech(text, selectedVoice)
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
        </Paper>
      </Container>
    </ThemeProvider>
  )
}

export default App
