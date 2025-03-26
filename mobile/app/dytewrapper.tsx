// DyteWrapper.jsx
import React, { useEffect, useState, useRef } from 'react';
import { Platform, View } from 'react-native';
import { ThemedText } from '@/components/ThemedText';

const DyteWrapper = ({ meetingId, authToken, participantName, onSessionEnd }) => {
  const [dyteLoaded, setDyteLoaded] = useState(false);
  const [meeting, setMeeting] = useState(null);
  const [error, setError] = useState(null);
  const [loadingState, setLoadingState] = useState('Starting...');
  const containerRef = useRef(null);

  // For web platform
  if (Platform.OS === 'web') {
    // Load Dyte scripts
    useEffect(() => {
      console.log('Loading Dyte web SDK scripts');
      setLoadingState('Loading Dyte SDK...');

      if (typeof window !== 'undefined' && !window.DyteClient) {
        const coreScript = document.createElement('script');
        coreScript.src = 'https://cdn.dyte.in/core/dyte.js';

        coreScript.onload = () => {
          console.log('Dyte Core SDK loaded successfully');
          const uiScript = document.createElement('script');
          uiScript.type = 'module';
          uiScript.innerHTML = `
            import { defineCustomElements } from 'https://cdn.jsdelivr.net/npm/@dytesdk/ui-kit/loader/index.es2017.js';
            defineCustomElements().then(() => {
              document.dispatchEvent(new Event('dyte-ui-loaded'));
            });
          `;

          document.head.appendChild(uiScript);
          document.addEventListener('dyte-ui-loaded', () => {
            console.log('All Dyte scripts loaded successfully');
            setDyteLoaded(true);
          }, { once: true });
        };

        coreScript.onerror = (e) => {
          console.error('Failed to load Dyte Core script', e);
          setError('Failed to load Dyte SDK');
        };

        document.head.appendChild(coreScript);
        return () => {
          if (document.head.contains(coreScript)) {
            document.head.removeChild(coreScript);
          }
        };
      } else if (window.DyteClient) {
        console.log('Dyte Core SDK already loaded');
        setDyteLoaded(true);
      }
    }, []);

    // Get a new token and initialize meeting
    useEffect(() => {
      if (!dyteLoaded || !meetingId || !authToken) return;

      const setupMeeting = async () => {
        try {
          setLoadingState('Connecting to meeting...');
          console.log('Initializing meeting with token:', authToken);

          // Initialize meeting with the provided authToken
          const dyteClient = await window.DyteClient.init({
            authToken,
            roomName: meetingId,
            defaults: {
              audio: true,
              video: true,
            },
            config: {
              roomConfig: {
                enableAudio: true,
                enableVideo: true,
              },
              // Remove custom designTokens from here - they should come from the preset
            }
          });

          // Join the meeting
          console.log('Joining meeting room...');
          await dyteClient.joinRoom();
          console.log('Successfully joined meeting room');

          setMeeting(dyteClient);
          setLoadingState('Creating UI...');

        } catch (error) {
          console.error('Setup error:', error);
          setError(`Setup failed: ${error.message}`);
        }
      };

      setupMeeting();
    }, [dyteLoaded, meetingId, authToken]);

    // Create UI when meeting is ready
    useEffect(() => {
      if (!meeting || !containerRef.current) return;

      try {
        const container = containerRef.current;

        // Clear container
        while (container.firstChild) {
          container.removeChild(container.firstChild);
        }

        // Create meeting UI
        const meetingEl = document.createElement('dyte-meeting');
        meetingEl.setAttribute('style', 'height: 100%; width: 100%;');
        meetingEl.meeting = meeting;

        // Set UI config to avoid preset errors
        meetingEl.config = {
          showSetupScreen: true,
          designTokens: {
            logo: "",
            borderRadius: "8px",
            backgroundColor: "#000000",
            textColor: "#ffffff",
            primaryColor: "#0b8484",
          }
        };

        // Listen for meeting end
        meeting.self.on('roomLeft', () => {
          console.log('User left the meeting');
          if (onSessionEnd) onSessionEnd();
        });

        container.appendChild(meetingEl);
        setLoadingState('Connected');

      } catch (uiError) {
        console.error('UI error:', uiError);
        setError(`UI error: ${uiError.message}`);
      }
    }, [meeting, onSessionEnd]);

    // Cleanup
    useEffect(() => {
      return () => {
        if (meeting) {
          console.log('Cleaning up meeting');
          try {
            meeting.leaveRoom();
          } catch (e) {
            console.error('Error leaving room:', e);
          }
        }
      };
    }, [meeting]);

    return (
      <View style={{ flex: 1, width: '100%', height: '100%' }}>
        {error ? (
          <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
            <ThemedText style={{ fontSize: 16, color: 'red', textAlign: 'center', marginBottom: 10 }}>
              Error: {error}
            </ThemedText>
          </View>
        ) : (
          <View style={{ flex: 1, width: '100%', height: '100%' }}>
            {!meeting ? (
              <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
                <ThemedText style={{ fontSize: 16, marginBottom: 8 }}>{loadingState}</ThemedText>
              </View>
            ) : (
              <>
                <div ref={containerRef} style={{ width: '100%', height: '100%' }}></div>
                {/* Status indicator */}
                <View style={{ position: 'absolute', top: 10, left: 10, backgroundColor: 'rgba(0,0,0,0.5)', padding: 8, borderRadius: 4 }}>
                  <ThemedText style={{ color: 'white' }}>Status: {meeting.connectionState}</ThemedText>
                </View>
              </>
            )}
          </View>
        )}
      </View>
    );
  }

  // Native implementation (unchanged)
  const { useDyteClient } = require('@dytesdk/react-native-core');
  const { DyteMeeting } = require('@dytesdk/react-native-ui-kit');

  const NativeDyteMeeting = () => {
    const [clientMeeting, initMeeting] = useDyteClient();
    const [isInitialized, setIsInitialized] = useState(false);

    useEffect(() => {
      const init = async () => {
        try {
          if (authToken && meetingId) {
            await initMeeting({
              authToken,
              roomName: meetingId,
            });
            setIsInitialized(true);
          }
        } catch (error) {
          console.error('Failed to initialize Dyte meeting:', error);
        }
      };

      init();

      return () => {
        if (clientMeeting) {
          clientMeeting.leaveRoom();
        }
      };
    }, [meetingId, authToken]);

    return isInitialized ? (
      <DyteMeeting meeting={clientMeeting} />
    ) : (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ThemedText>Connecting to session...</ThemedText>
      </View>
    );
  };

  return <NativeDyteMeeting />;
};

export default DyteWrapper;