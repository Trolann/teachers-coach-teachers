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
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Byb250by5nZXRzdHJlYW0uaW8iLCJzdWIiOiJ1c2VyL1NoYWFrX1RpIiwidXNlcl9pZCI6IlNoYWFrX1RpIiwidmFsaWRpdHlfaW5fc2Vjb25kcyI6NjA0ODAwLCJpYXQiOjE3NDQ4OTYyOTQsImV4cCI6MTc0NTUwMTA5NH0.71ZgMlOs_6lSzcn8hwBIVJNL-vCxx0j7aoT0L7-9lvg'; // the token can be found in the "Credentials" section
const userId = 'Shaak_Ti'; // the user id can be found in the "Credentials" section
const callId = 'l6K7VihoMt64';

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
      pathname: '/HomeScreen',
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
