import React from 'react';
import { StyleSheet, TouchableOpacity, View, Alert } from 'react-native';
import { Href, useRouter } from 'expo-router';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import sendAlert from './utils/alerts';
import TokenManager from './auth/TokenManager';
import { Platform } from 'react-native';

export default function PreApplicationScreen() {
  const router = useRouter();

  const handleRoleSelection = async (role: 'mentor' | 'mentee') => {
    try {
      console.log('Selected role:', role);
      await TokenManager.getInstance().setUserRole(role);
  
      const storedRole = await TokenManager.getInstance().getUserRole();
      console.log('Stored role:', storedRole);
  
      if (storedRole === role) {
        console.log('Role successfully stored!');
      } else {
        console.error('Role storage mismatch!');
      }
  
      // Define redirectPath before using it
      const redirectPath = role === 'mentor' ? '/mentor-application' : '/mentee-application';
  
      const message = `Welcome! You've been registered as a ${role}. Please fill out an application to join.`;
  
      if (Platform.OS === 'web') {
        alert(message);
        router.replace(redirectPath);
      } else {
        Alert.alert(
          "Success 🎉",
          message,
          [
            {
              text: "Continue",
              onPress: () => {
                router.replace(redirectPath);
              },
            }
          ]
        );
      }
  
    } catch (error) {
      console.error('Role selection failed:', error);
      sendAlert("Error", "Failed to set user role. Please try again.");
    }
  };

  return (
    <ThemedView style={styles.container}>
      <View style={styles.card}>
        {/* Logo/Icon placeholder */}
        <View style={styles.logoContainer}>
          <View style={styles.logo} />
        </View>

        {/* Welcome Text */}
        <View style={styles.welcomeContainer}>
          <ThemedText style={styles.welcomeText}>
            We're happy to see you 🙂
          </ThemedText>
          <ThemedText style={styles.descriptionText}>
            You are about to embark on a journey of professional development and collaboration.
            Before we begin, please select whether you'd like to continue as a mentor or a mentee.
          </ThemedText>
        </View>

        {/* Selection Buttons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.selectionButton, styles.mentorButton]}
            onPress={() => handleRoleSelection('mentor')}
          >
            <ThemedText style={styles.buttonText}>Continue as a Mentor 🍎</ThemedText>
          </TouchableOpacity>

          <View style={styles.dividerContainer}>
            <View style={styles.divider} />
            <ThemedText style={styles.dividerText}>or</ThemedText>
            <View style={styles.divider} />
          </View>

          <TouchableOpacity
            style={[styles.selectionButton, styles.menteeButton]}
            onPress={() => handleRoleSelection('mentee')}
          >
            <ThemedText style={styles.buttonText}>Continue as a Mentee 🎓</ThemedText>
          </TouchableOpacity>
        </View>
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 25,
    paddingVertical: 120,
    paddingHorizontal: 30,
    width: '100%',
    flexGrow: 1,
    justifyContent: 'space-between',
    alignItems: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 5 },
    shadowRadius: 10,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  logo: {
    width: 80,
    height: 80,
    borderWidth: 2,
    borderColor: '#000',
    borderRadius: 16,
  },
  welcomeContainer: {
    alignItems: 'center',
    marginBottom: 45,
    paddingHorizontal: 20,
  },
  welcomeText: {
    fontSize: 23.95,
    fontWeight: '700',
    color: '#2B2D42',
    marginBottom: 15,
    lineHeight: 40,
    textAlign: 'center',
  },
  descriptionText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 30,
    maxWidth: '100%',
  },
  buttonContainer: {
    width: '100%',
    maxWidth: 400,
    gap: 10,
  },
  selectionButton: {
    paddingVertical: 16,
    borderRadius: 30,
    alignItems: 'center',
    width: '100%',
    elevation: 3,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 6,
  },
  mentorButton: {
    backgroundColor: '#4CAF50',
  },
  menteeButton: {
    backgroundColor: '#007BFF',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 10,
    width: '100%',
  },
  divider: {
    flex: 1,
    height: 1,
    backgroundColor: '#ddd',
  },
  dividerText: {
    marginHorizontal: 10,
    color: '#848282',
    fontSize: 16,
    fontWeight: '500',
  },
});
