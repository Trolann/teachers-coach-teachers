import React, { useState } from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { HomeScreen } from './HomeScreen';
import { CallScreen } from './CallScreen';

// 1. Import the StreamVideo and StreamVideoClient components
import {
  StreamVideo,
  StreamVideoClient,
} from '@stream-io/video-react-native-sdk';
import { router, useLocalSearchParams } from 'expo-router';

// 2. Create a StreamVideoClient instance
const apiKey = 'mmhfdzb5evj2'; // the API key can be found in the "Credentials" section
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Byb250by5nZXRzdHJlYW0uaW8iLCJzdWIiOiJ1c2VyL0dlbmVyYWxfVmVlcnMiLCJ1c2VyX2lkIjoiR2VuZXJhbF9WZWVycyIsInZhbGlkaXR5X2luX3NlY29uZHMiOjYwNDgwMCwiaWF0IjoxNzQ3MDUzMjIxLCJleHAiOjE3NDc2NTgwMjF9.ndfW2RquLjDwzSNCOlJ6AqD0gPkobUNomOvrSSQeVPM'; // the token can be found in the "Credentials" section
const userId = 'General_Veers'; // the user id can be found in the "Credentials" section
const callId = 'v1pIDkbkpC0o';

// 3. Create a user object
const user = {
  id: userId,
  name: 'John Malkovich',
  image: `https://getstream.io/random_png/?id=${userId}&name=John+Malkovich`,
};
// 4. Create a StreamVideoClient instance
const client = new StreamVideoClient({ apiKey, user, token });

export default function App() {

  // console.log(imagePath);

  const [activeScreen, setActiveScreen] = useState('home');

  const goToCallScreen = () => setActiveScreen('call-screen');
  const goToHomeScreen = () => {
    setActiveScreen('home');
    router.push({
      pathname: '/mentee-matching',
    });
  };
  return (
    // 5. Wrap your app with the StreamVideo component
    <StreamVideo client={client}>
      <SafeAreaView style={styles.container}>
        {activeScreen === 'call-screen' ? (
          <CallScreen goToHomeScreen={goToHomeScreen} callId={callId} />
        ) : (
          <HomeScreen goToCallScreen={goToCallScreen} />
        )}
      </SafeAreaView>
    </StreamVideo>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    textAlign: 'center',
  },
});
