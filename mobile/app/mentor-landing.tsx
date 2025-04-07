import React, { useState } from 'react';
import { View, Text, Switch, StyleSheet, Image } from 'react-native';

const MentorLandingScreen = () => {
  const [isOnline, setIsOnline] = useState(false);

  const toggleSwitch = () => setIsOnline(previousState => !previousState);

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hi, Susie 👋</Text>
          <Text style={styles.subtext}>Are you ready to mentor?</Text>
        </View>
        <Image
          source={require('../assets/images/mentor-profile-picture.png')} // Replace profile picture of the user stored within our database
          style={styles.profileImage}
        />
      </View>

      {/* Toggle */}
      <View style={styles.toggleContainer}>
        <Text style={styles.togglePrompt}>Ready to Mentor?</Text>
        <Text style={styles.toggleSubtext}>
          Click the toggle button to indicate you are online
        </Text>
        <Switch
          trackColor={{ false: '#767577', true: '#C7F9CC' }}
          thumbColor={isOnline ? '#34C759' : '#f4f3f4'}
          ios_backgroundColor="#3e3e3e"
          onValueChange={toggleSwitch}
          value={isOnline}
        />
      </View>
    </View>
  );
};

export default MentorLandingScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 24,
    justifyContent: 'flex-start',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 40,
  },
  greeting: {
    fontSize: 28,
    fontWeight: '600',
  },
  subtext: {
    fontSize: 18,
    color: '#555',
  },
  profileImage: {
    width: 80,
    height: 80,
    borderRadius: 44,
  },
  toggleContainer: {
    alignItems: 'center',
    marginTop: 60,
  },
  togglePrompt: {
    fontSize: 28,
    fontWeight: '600',
    marginBottom: 8,
  },
  toggleSubtext: {
    fontSize: 18,
    color: '#777',
    textAlign: 'center',
    marginBottom: 16,
  },
});
