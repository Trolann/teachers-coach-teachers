// import React, { useEffect, useState } from 'react';
// import { StyleSheet, TouchableOpacity, View, Alert, Platform } from 'react-native';
// import { useRouter } from 'expo-router';
// import { ThemedView } from '@/components/ThemedView';
// import { ThemedText } from '@/components/ThemedText';
// import { Ionicons } from '@expo/vector-icons';
// import TokenManager from '@/app/auth/TokenManager';

// // Import Dyte SDK components
// import {
//     DyteProvider,
//     useDyteClient,
//   } from '@dytesdk/react-native-core';
//   import { DyteMeeting } from '@dytesdk/react-native-ui-kit';

// // Session component that handles the Dyte meeting
// const DyteMeetingComponent = ({ meetingId, authToken, onSessionEnd }) => {
//   const [meeting, initMeeting] = useDyteClient();
//   const [isInitialized, setIsInitialized] = useState(false);

//   useEffect(() => {
//     // Initialize Dyte meeting when component mounts
//     const init = async () => {
//       try {
//         if (authToken && meetingId) {
//           await initMeeting({
//             authToken,
//             roomName: meetingId,
//             // Add any additional config options needed
//           });
//           setIsInitialized(true);
//         }
//       } catch (error) {
//         console.error('Failed to initialize Dyte meeting:', error);
//         Alert.alert('Error', 'Failed to connect to session. Please try again.');
//       }
//     };

//     init();

//     // Cleanup function
//     return () => {
//       if (meeting) {
//         meeting.leaveRoom();
//       }
//     };
//   }, [meetingId, authToken, initMeeting]);

//   return isInitialized ? (
//     <DyteMeeting meeting={meeting} />
//   ) : (
//     <View style={styles.loadingContainer}>
//       <ThemedText>Connecting to session...</ThemedText>
//     </View>
//   );
// };

// export default function MentorshipSessionScreen() {
//   const router = useRouter();
//   const [meetingDetails, setMeetingDetails] = useState({
//     meetingId: '',
//     authToken: '',
//     participantName: '',
//   });
//   const [elapsedTime, setElapsedTime] = useState(0);
//   const [isLoading, setIsLoading] = useState(true);
//   const [sessionInfo, setSessionInfo] = useState({
//     mentorName: 'Melissa Crawford',
//     sessionDuration: 30, // in minutes
//   });

//   // Format elapsed time to MM:SS format
//   const formatTime = (seconds) => {
//     const mins = Math.floor(seconds / 60);
//     const secs = seconds % 60;
//     return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
//   };

//   useEffect(() => {
//     // Mock loading meeting details
//     // TODO: in future, fetch these from backend
//     const fetchMeetingDetails = async () => {
//       try {
//         // TODO: Replace with actual API call to get Dyte meeting details
//         setMeetingDetails({
//           meetingId: 'mock-meeting-id',
//           authToken: 'mock-auth-token',
//           participantName: 'Steve', // TODO: bring from users profile
//         });

//         // Start the timer for session duration
//         const interval = setInterval(() => {
//           setElapsedTime((prevTime) => prevTime + 1);
//         }, 1000);

//         // Simulate loading delay
//         setTimeout(() => {
//           setIsLoading(false);
//         }, 1500);

//         return () => clearInterval(interval);
//       } catch (error) {
//         console.error('Error fetching meeting details:', error);
//         Alert.alert('Error', 'Failed to load session details');
//       }
//     };

//     fetchMeetingDetails();
//   }, []);

//   const handleEndSession = () => {
//     Alert.alert(
//       'End Session',
//       'Are you sure you want to end this session?',
//       [
//         {
//           text: 'Cancel',
//           style: 'cancel',
//         },
//         {
//           text: 'End',
//           onPress: () => {
//             // Handle session end logic here
//             router.replace('/(tabs)');
//           },
//           style: 'destructive',
//         },
//       ]
//     );
//   };

//   const handleRequestExtension = () => {
//     Alert.alert(
//       'Request Extension',
//       'Would you like to request a 15-minute extension?',
//       [
//         {
//           text: 'Cancel',
//           style: 'cancel',
//         },
//         {
//           text: 'Request',
//           onPress: () => {
//             // Handle extension request logic here
//             Alert.alert('Extension Requested', 'Your request has been sent to the mentor.');
//           },
//         },
//       ]
//     );
//   };

//   return (
//     <ThemedView style={styles.container}>
//       <View style={styles.header}>
//         <ThemedText style={styles.welcomeText}>
//           Hi, Steve <ThemedText style={styles.waveEmoji}>👋</ThemedText>
//         </ThemedText>
//         <View style={styles.profileCircle}>
//           <ThemedText style={styles.notificationCount}>12</ThemedText>
//         </View>
//       </View>

//       <ThemedText style={styles.sessionTitle}>
//         Session with {sessionInfo.mentorName}
//       </ThemedText>

//       <View style={styles.timerContainer}>
//         <Ionicons name="time-outline" size={20} color="#848282" />
//         <ThemedText style={styles.timerText}>{formatTime(elapsedTime)}</ThemedText>
//       </View>

//       <View style={styles.videoContainer}>
//         {isLoading ? (
//           <View style={styles.placeholderContainer}>
//             <ThemedText style={styles.placeholderText}>
//               Connecting to session...
//             </ThemedText>
//           </View>
//         ) : (
//         //   <DyteProvider value={meetingDetails}>
//         //     <View style={styles.mainVideoFeed}>
//         //       <ThemedText style={styles.placeholderText}>
//         //         Main Video Feed
//         //       </ThemedText>
//         //       <ThemedText style={styles.subtitleText}>
//         //         (Video feed would be embedded here)
//         //       </ThemedText>
//         //     </View>
//         //     <View style={styles.selfViewContainer}>
//         //       <ThemedText style={styles.selfViewText}>Self View</ThemedText>
//         //     </View>
//         //   </DyteProvider>
//             <DyteMeetingComponent 
//                 meetingId={meetingDetails.meetingId}
//                 authToken={meetingDetails.authToken}
//                 onSessionEnd={handleEndSession}
//             />
//         )}
//       </View>

//       <View style={styles.bottomActions}>
//         <TouchableOpacity style={styles.extensionButton} onPress={handleRequestExtension}>
//           <ThemedText style={styles.extensionButtonText}>Request Extension</ThemedText>
//         </TouchableOpacity>
        
//         <TouchableOpacity style={styles.endButton} onPress={handleEndSession}>
//           <ThemedText style={styles.endButtonText}>End Session</ThemedText>
//         </TouchableOpacity>
//       </View>

//       <View style={styles.navigationBar}>
//         <TouchableOpacity style={[styles.navButton, styles.activeNavButton]}>
//           <Ionicons name="home" size={24} color="#FF6B6B" />
//         </TouchableOpacity>
//         <TouchableOpacity style={styles.navButton}>
//           <Ionicons name="time-outline" size={24} color="#848282" />
//         </TouchableOpacity>
//         <TouchableOpacity style={styles.navButton}>
//           <Ionicons name="heart-outline" size={24} color="#848282" />
//         </TouchableOpacity>
//         <TouchableOpacity style={styles.navButton}>
//           <Ionicons name="person-outline" size={24} color="#848282" />
//         </TouchableOpacity>
//       </View>
//     </ThemedView>
//   );
// }

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//     backgroundColor: '#FFFFFF',
//     padding: 20,
//   },
//   header: {
//     flexDirection: 'row',
//     justifyContent: 'space-between',
//     alignItems: 'center',
//     marginBottom: 20,
//   },
//   welcomeText: {
//     fontSize: 28,
//     fontWeight: '600',
//     color: '#333333',
//   },
//   waveEmoji: {
//     fontSize: 28,
//   },
//   profileCircle: {
//     width: 40,
//     height: 40,
//     borderRadius: 20,
//     backgroundColor: '#F0F0F0',
//     justifyContent: 'center',
//     alignItems: 'center',
//   },
//   notificationCount: {
//     fontSize: 14,
//     fontWeight: '500',
//     color: '#666666',
//   },
//   sessionTitle: {
//     fontSize: 22,
//     fontWeight: '500',
//     color: '#333333',
//     marginBottom: 10,
//   },
//   timerContainer: {
//     flexDirection: 'row',
//     alignItems: 'center',
//     marginBottom: 15,
//   },
//   timerText: {
//     marginLeft: 5,
//     fontSize: 16,
//     color: '#666666',
//   },
//   videoContainer: {
//     flex: 1,
//     backgroundColor: '#E5E5E5',
//     borderRadius: 15,
//     overflow: 'hidden',
//     position: 'relative',
//     marginBottom: 20,
//   },
//   loadingContainer: {
//     flex: 1,
//     justifyContent: 'center',
//     alignItems: 'center',
//   },
//   placeholderContainer: {
//     flex: 1,
//     justifyContent: 'center',
//     alignItems: 'center',
//   },
//   placeholderText: {
//     fontSize: 18,
//     color: '#888888',
//     textAlign: 'center',
//   },
//   subtitleText: {
//     fontSize: 14,
//     color: '#888888',
//     textAlign: 'center',
//   },
//   mainVideoFeed: {
//     flex: 1,
//     justifyContent: 'center',
//     alignItems: 'center',
//   },
//   selfViewContainer: {
//     position: 'absolute',
//     width: 200,
//     height: 200,
//     bottom: 20,
//     right: 20,
//     backgroundColor: '#333333',
//     borderRadius: 10,
//     justifyContent: 'center',
//     alignItems: 'center',
//   },
//   selfViewText: {
//     color: '#FFFFFF',
//     fontSize: 16,
//   },
//   bottomActions: {
//     flexDirection: 'row',
//     justifyContent: 'space-between',
//     marginBottom: 20,
//   },
//   extensionButton: {
//     backgroundColor: '#F5F5F5',
//     paddingVertical: 14,
//     paddingHorizontal: 20,
//     borderRadius: 25,
//     flex: 1,
//     marginRight: 10,
//     alignItems: 'center',
//   },
//   extensionButtonText: {
//     color: '#666666',
//     fontWeight: '500',
//     fontSize: 16,
//   },
//   endButton: {
//     backgroundColor: '#FF6B6B',
//     paddingVertical: 14,
//     paddingHorizontal: 20,
//     borderRadius: 25,
//     flex: 1,
//     marginLeft: 10,
//     alignItems: 'center',
//   },
//   endButtonText: {
//     color: 'white',
//     fontWeight: '500',
//     fontSize: 16,
//   },
//   navigationBar: {
//     flexDirection: 'row',
//     justifyContent: 'space-around',
//     paddingVertical: 15,
//     borderTopWidth: 1,
//     borderTopColor: '#E5E5E5',
//   },
//   navButton: {
//     padding: 10,
//   },
//   activeNavButton: {
//     backgroundColor: '#F8F8F8',
//     borderRadius: 50,
//   },
// });
import React, { useEffect, useState } from 'react';
import { StyleSheet, TouchableOpacity, View, Alert, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import { Ionicons } from '@expo/vector-icons';

// Import Dyte SDK components
import {
  DyteProvider,
  useDyteClient,
} from '@dytesdk/react-native-core';
import { DyteUIProvider, DyteMeeting } from '@dytesdk/react-native-ui-kit';

// The actual meeting component that will render the Dyte UI
const DyteMeetingComponent = ({ authToken, onSessionEnd }) => {
  const [meeting, initMeeting] = useDyteClient();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const init = async () => {
      try {
        if (authToken) {
          await initMeeting({
            authToken,
            defaults: {
              audio: true,
              video: true,
            },
          });
          setIsInitialized(true);
        }
      } catch (error) {
        console.error('Failed to initialize Dyte meeting:', error);
        Alert.alert('Error', 'Failed to connect to session. Please try again.');
      }
    };

    init();

    // Cleanup function
    return () => {
      if (meeting) {
        // Properly leave the meeting on component unmount
        meeting.leaveRoom();
      }
    };
  }, [authToken, initMeeting]);

  // Don't render DyteMeeting until the meeting is initialized
  if (!isInitialized || !meeting) {
    return (
      <View style={styles.loadingContainer}>
        <ThemedText>Initializing meeting...</ThemedText>
      </View>
    );
  }

  return (
    <DyteProvider value={meeting}>
      <DyteUIProvider>
        <DyteMeeting meeting={meeting} />
      </DyteUIProvider>
    </DyteProvider>
  );
};

export default function MentorshipSessionScreen() {
  const router = useRouter();
  const [authToken, setAuthToken] = useState('');
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [sessionInfo, setSessionInfo] = useState({
    mentorName: 'Melissa Crawford',
    sessionDuration: 30, // in minutes
  });

  // Format elapsed time to MM:SS format
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  useEffect(() => {
    // Mock loading meeting details
    // In production, fetch these from your backend
    const fetchMeetingDetails = async () => {
      try {
        // Simulate API call to get Dyte meeting details
        // In production, replace with actual API call
        setTimeout(() => {
          setAuthToken('your-auth-token-from-backend');
          setIsLoading(false);
        }, 1500);

        // Start the timer for session duration
        const interval = setInterval(() => {
          setElapsedTime((prevTime) => prevTime + 1);
        }, 1000);

        return () => clearInterval(interval);
      } catch (error) {
        console.error('Error fetching meeting details:', error);
        Alert.alert('Error', 'Failed to load session details');
      }
    };

    fetchMeetingDetails();
  }, []);

  const handleEndSession = () => {
    Alert.alert(
      'End Session',
      'Are you sure you want to end this session?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'End',
          onPress: () => {
            // Handle session end logic here
            router.replace('/(tabs)');
          },
          style: 'destructive',
        },
      ]
    );
  };

  const handleRequestExtension = () => {
    Alert.alert(
      'Request Extension',
      'Would you like to request a 15-minute extension?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Request',
          onPress: () => {
            // Handle extension request logic here
            Alert.alert('Extension Requested', 'Your request has been sent to the mentor.');
          },
        },
      ]
    );
  };

  return (
    <ThemedView style={styles.container}>
      <View style={styles.header}>
        <ThemedText style={styles.welcomeText}>
          Hi, Steve <ThemedText style={styles.waveEmoji}>👋</ThemedText>
        </ThemedText>
        <View style={styles.profileCircle}>
          <ThemedText style={styles.notificationCount}>12</ThemedText>
        </View>
      </View>

      <ThemedText style={styles.sessionTitle}>
        Session with {sessionInfo.mentorName}
      </ThemedText>

      <View style={styles.timerContainer}>
        <Ionicons name="time-outline" size={20} color="#848282" />
        <ThemedText style={styles.timerText}>{formatTime(elapsedTime)}</ThemedText>
      </View>

      <View style={styles.videoContainer}>
        {isLoading ? (
          <View style={styles.placeholderContainer}>
            <ThemedText style={styles.placeholderText}>
              Connecting to session...
            </ThemedText>
          </View>
        ) : (
          <DyteMeetingComponent 
            authToken={authToken}
            onSessionEnd={handleEndSession}
          />
        )}
      </View>

      <View style={styles.bottomActions}>
        <TouchableOpacity style={styles.extensionButton} onPress={handleRequestExtension}>
          <ThemedText style={styles.extensionButtonText}>Request Extension</ThemedText>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.endButton} onPress={handleEndSession}>
          <ThemedText style={styles.endButtonText}>End Session</ThemedText>
        </TouchableOpacity>
      </View>

      <View style={styles.navigationBar}>
        <TouchableOpacity style={[styles.navButton, styles.activeNavButton]}>
          <Ionicons name="home" size={24} color="#FF6B6B" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.navButton}>
          <Ionicons name="time-outline" size={24} color="#848282" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.navButton}>
          <Ionicons name="heart-outline" size={24} color="#848282" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.navButton}>
          <Ionicons name="person-outline" size={24} color="#848282" />
        </TouchableOpacity>
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  welcomeText: {
    fontSize: 28,
    fontWeight: '600',
    color: '#333333',
  },
  waveEmoji: {
    fontSize: 28,
  },
  profileCircle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F0F0F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationCount: {
    fontSize: 14,
    fontWeight: '500',
    color: '#666666',
  },
  sessionTitle: {
    fontSize: 22,
    fontWeight: '500',
    color: '#333333',
    marginBottom: 10,
  },
  timerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  timerText: {
    marginLeft: 5,
    fontSize: 16,
    color: '#666666',
  },
  videoContainer: {
    flex: 1,
    backgroundColor: '#E5E5E5',
    borderRadius: 15,
    overflow: 'hidden',
    position: 'relative',
    marginBottom: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  placeholderText: {
    fontSize: 18,
    color: '#888888',
    textAlign: 'center',
  },
  bottomActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  extensionButton: {
    backgroundColor: '#F5F5F5',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 25,
    flex: 1,
    marginRight: 10,
    alignItems: 'center',
  },
  extensionButtonText: {
    color: '#666666',
    fontWeight: '500',
    fontSize: 16,
  },
  endButton: {
    backgroundColor: '#FF6B6B',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 25,
    flex: 1,
    marginLeft: 10,
    alignItems: 'center',
  },
  endButtonText: {
    color: 'white',
    fontWeight: '500',
    fontSize: 16,
  },
  navigationBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 15,
    borderTopWidth: 1,
    borderTopColor: '#E5E5E5',
  },
  navButton: {
    padding: 10,
  },
  activeNavButton: {
    backgroundColor: '#F8F8F8',
    borderRadius: 50,
  },
});