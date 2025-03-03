import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Image, StyleSheet, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';


export default function FindMentorScreen() {
  const [goal, setGoal] = useState('');
  const router = useRouter();
  return (
    <SafeAreaView style={styles.container}>
      {/* Main Content */}
      <View style={styles.content}>
        {/* Header Section */}
        <View style={styles.header}>
          <Text style={styles.greeting}>
            Hi, Steve <Text style={styles.wave}>👋</Text>
          </Text>
          <Image 
            source={require('../assets/images/stock_pfp.jpeg')}
            style={styles.profileImage}
          />
        </View>
        <Text style={styles.subtitle}>What kind of help do you need?</Text>

        <View style={styles.mentorContainer}>
          <Text style={styles.title}>Find a Mentor</Text>
          <Text style={styles.label}>Briefly describe what your goal is for this session</Text>
          <TextInput
            style={styles.input}
            placeholder="Lorem Ipsum..."
            placeholderTextColor="#999"
            multiline
            value={goal}
            onChangeText={setGoal}
          />
          <TouchableOpacity 
            style={styles.button}
            onPress={() => router.push('/mentee-matching')}
          >
            <Text style={styles.buttonText}>Find a Mentor</Text>
            <Ionicons name="paper-plane-outline" size={20} color="white" style={styles.buttonIcon} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Bottom Navigation (No Padding) */}
      <View style={styles.navbar}>
        <Ionicons name="home" size={24} color="black" />
        <Ionicons name="time-outline" size={24} color="gray" />
        <Ionicons name="heart-outline" size={24} color="gray" />
        <Ionicons name="person-outline" size={24} color="gray" />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1, 
    backgroundColor: 'white',
  },
  content: {
    flex: 1, 
    paddingHorizontal: 20, 
    paddingTop: 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  mentorContainer: {
    flex: 1, 
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: -60, 
  },
  greeting: {
    fontSize: 30,
    fontWeight: 'bold',
  },
  wave: {
    fontSize: 30,
  },
  profileImage: {
    width: 45,
    height: 45,
    borderRadius: 25,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  input: {
    height: 80,
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingTop: 10,
    textAlignVertical: 'top',
    backgroundColor: '#f9f9f9',
    marginBottom: 20,
    width: '100%',
  },
  button: {
    flexDirection: 'row',
    backgroundColor: 'black',
    padding: 15,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonIcon: {
    marginLeft: 10,
  },
  navbar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: 15,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderColor: '#ddd',
  },
});
