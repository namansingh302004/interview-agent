import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent, ConnectionState, DisconnectReason } from 'livekit-client';
import './App.css';

function App() {
  const [room, setRoom] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [currentRoom, setCurrentRoom] = useState('');
  const [logs, setLogs] = useState([]);
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [error, setError] = useState('');

  const roomRef = useRef(null);

  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    setLogs(prev => [...prev, logEntry]);
    console.log(logEntry);
  };

  const generateFreshToken = async (roomName) => {
    try {
      const response = await fetch(
        `http://localhost:8000/generate-token?room=${encodeURIComponent(roomName)}&participant_name=candidate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      addLog(`✅ Fresh token generated (expires in ${data.expires_in} seconds)`);
      return data;
    } catch (error) {
      addLog(`❌ Token generation failed: ${error.message}`);
      throw error;
    }
  };

  const createRoom = async () => {
    try {
      const response = await fetch('http://localhost:8000/create-room', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.room_name;
    } catch (error) {
      addLog(`❌ Room creation failed: ${error.message}`);
      throw error;
    }
  };

  const connectToRoom = async () => {
    if (isConnecting || isConnected) return;

    setIsConnecting(true);
    setError('');

    try {
      // Create a new room
      addLog('Creating interview room...');
      const roomName = await createRoom();
      setCurrentRoom(roomName);
      addLog(`Room created: ${roomName}`);

      // Generate fresh token
      const tokenData = await generateFreshToken(roomName);

      // Create new room instance
      const newRoom = new Room({
        adaptiveStream: true,
        dynacast: true,
        videoCaptureDefaults: {
          resolution: {
            width: 1280,
            height: 720,
          },
        },
      });

      roomRef.current = newRoom;
      setRoom(newRoom);

      // Set up event listeners
      newRoom.on(RoomEvent.Connected, () => {
        addLog('✅ Connected to LiveKit room');
        setIsConnected(true);
        setIsConnecting(false);
      });

      newRoom.on(RoomEvent.Disconnected, (reason) => {
        addLog(`Disconnected: ${reason}`);
        setIsConnected(false);
        setIsConnecting(false);
        if (reason !== DisconnectReason.CLIENT_INITIATED) {
          setError(`Connection lost: ${reason}`);
        }
      });

      newRoom.on(RoomEvent.ConnectionStateChanged, (state) => {
        addLog(`Connection state: ${state}`);
        if (state === ConnectionState.Reconnecting) {
          addLog('Attempting to reconnect...');
        }
      });

      newRoom.on(RoomEvent.ParticipantConnected, (participant) => {
        addLog(`✅ Participant joined: ${participant.identity}`);
      });

      newRoom.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        if (track.kind === 'audio') {
          addLog(`🔊 Audio track received from ${participant.identity}`);
          const audioElement = track.attach();
          audioElement.play().catch(e => {
            addLog(`Audio autoplay blocked: ${e.message}`);
          });
        }
      });

      // Connect to room
      addLog('Connecting to LiveKit...');
      await newRoom.connect(tokenData.url, tokenData.token);

      // Enable microphone
      if (audioEnabled) {
        await enableMicrophone(newRoom);
      }

    } catch (error) {
      addLog(`❌ Connection failed: ${error.message}`);
      setError(error.message);
      setIsConnecting(false);
    }
  };

  const enableMicrophone = async (roomInstance = room) => {
    if (!roomInstance) return;

    try {
      addLog('🎤 Enabling microphone...');
      await roomInstance.localParticipant.enableCameraAndMicrophone(false, true);
      setAudioEnabled(true);
      addLog('✅ Microphone enabled');
    } catch (error) {
      addLog(`❌ Microphone error: ${error.message}`);
      setError(`Microphone access denied: ${error.message}`);
    }
  };

  const disconnect = () => {
    if (roomRef.current) {
      addLog('Disconnecting from room...');
      roomRef.current.disconnect();
      roomRef.current = null;
    }
    setRoom(null);
    setIsConnected(false);
    setIsConnecting(false);
    setCurrentRoom('');
    setAudioEnabled(false);
    setError('');
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect();
      }
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎤 AI Interview Assistant</h1>

        {/* Audio Visualizer - Show when connected and audio enabled */}
        {isConnected && audioEnabled && (
          <div className={`audio-visualizer ${isConnected && audioEnabled ? 'active' : ''}`}>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
            <div className="sound-bar"></div>
          </div>
        )}

        <div className="status-section">
          <div className={`status-indicator ${isConnected ? 'connected' : isConnecting ? 'connecting' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : isConnecting ? '🟡 Connecting...' : '🔴 Disconnected'}
          </div>

          {currentRoom && (
            <div className="room-info">
              Room: <code>{currentRoom}</code>
            </div>
          )}
        </div>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <div className="controls">
          {!isConnected && !isConnecting && (
            <button onClick={connectToRoom} className="primary-button">
              Start Interview
            </button>
          )}

          {isConnected && !audioEnabled && (
            <button onClick={() => enableMicrophone()} className="secondary-button">
              🎤 Enable Microphone
            </button>
          )}

          {isConnected && (
            <button onClick={disconnect} className="danger-button">
              End Interview
            </button>
          )}
        </div>

        <div className="instructions">
          {!isConnected && (
            <p>Click "Start Interview" to begin your AI-powered interview session.</p>
          )}
          {isConnected && !audioEnabled && (
            <p>Enable your microphone to start speaking with the AI interviewer.</p>
          )}
          {isConnected && audioEnabled && (
            <p>🎙️ You're live! The AI interviewer will ask you questions. Speak naturally.</p>
          )}
        </div>
      </header>

      <div className="logs-section">
        <h3>Interview Log</h3>
        <div className="logs">
          {logs.map((log, index) => (
            <div key={index} className="log-entry">
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;