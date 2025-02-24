import { useState, useEffect } from 'react'
import { FaPlay, FaStop, FaMicrophone } from 'react-icons/fa'
import apiService, { Voice } from './services/api'
import './App.css'

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
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-md overflow-hidden">
        <div className="p-8">
          <div className="flex items-center justify-center mb-6">
            <FaMicrophone className="text-indigo-600 text-3xl mr-3" />
            <h1 className="text-2xl font-bold text-gray-900">ElevenLabs Text-to-Speech</h1>
          </div>
          
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
              <p className="text-red-700">{error}</p>
            </div>
          )}
          
          <div className="mb-6">
            <label htmlFor="voice-select" className="block text-sm font-medium text-gray-700 mb-2">
              Select Voice
            </label>
            <select
              id="voice-select"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
            >
              {voices.map((voice) => (
                <option key={voice.voice_id} value={voice.voice_id}>
                  {voice.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-6">
            <label htmlFor="text-input" className="block text-sm font-medium text-gray-700 mb-2">
              Text to Convert
            </label>
            <textarea
              id="text-input"
              rows={5}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Enter text to convert to speech..."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>
          
          <div className="flex items-center justify-between">
            <button
              type="button"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              onClick={handleTextToSpeech}
              disabled={isLoading || !text.trim()}
            >
              {isLoading ? 'Converting...' : 'Convert to Speech'}
            </button>
            
            {audioUrl && (
              <div className="flex space-x-2">
                <button
                  type="button"
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  onClick={() => playAudio(audioUrl)}
                  disabled={isPlaying}
                >
                  <FaPlay className="mr-2" /> Play
                </button>
                {isPlaying && (
                  <button
                    type="button"
                    className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    onClick={stopAudio}
                  >
                    <FaStop className="mr-2" /> Stop
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
