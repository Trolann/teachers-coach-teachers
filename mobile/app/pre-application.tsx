import React from 'react';
import { StyleSheet, TouchableOpacity, View, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import TokenManager from './auth/TokenManager';
import { Href } from 'expo-router';
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
  
      const message = `Welcome! You've been registered as a ${role}.`;
  
      if (Platform.OS === 'web') {
        // ✅ Web uses browser's alert function
        alert(message);
        if (role === 'mentee') {
          router.replace('/pre-matching-mentee'); 
        } else {
          router.replace('/(tabs)');
        }
      } else {
        // ✅ Mobile uses React Native Alert
        Alert.alert(
          "Success",
          message,
          [
            {
              text: "Continue",
              onPress: () => {
                if (role === 'mentee') {
                  router.replace('/pre-matching-mentee'); 
                } else {
                  router.replace('/(tabs)'); 
                }
              },
            }
          ]
        );
      }
    } catch (error) {
      console.error('Role selection failed:', error);
      if (Platform.OS === 'web') {
        alert("Error: Failed to set user role. Please try again.");
      } else {
        Alert.alert("Error", "Failed to set user role. Please try again.");
      }
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
            We're happy to see you here.
          </ThemedText>
          <ThemedText style={styles.descriptionText}>
            You are about to embark on a journey of professional development and collaboration.
            Before we begin, please select whether you'd like to continue as a mentor or a mentee.
          </ThemedText>
        </View>

        {/* Selection Buttons */}
        <View style={styles.buttonContainer}>
          <TouchableOpacity 
            style={styles.selectionButton}
            onPress={() => handleRoleSelection('mentor')}
          >
            <ThemedText style={styles.buttonText}>Mentor</ThemedText>
          </TouchableOpacity>

          <View style={styles.dividerContainer}>
            <View style={styles.divider} />
            <ThemedText style={styles.dividerText}>or</ThemedText>
            <View style={styles.divider} />
          </View>

          <TouchableOpacity 
            style={styles.selectionButton}
            onPress={() => handleRoleSelection('mentee')}
          >
            <ThemedText style={styles.buttonText}>Mentee</ThemedText>
          </TouchableOpacity>
        </View>
      </View>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  card: {
    backgroundColor: 'white',
    margin: 20,
    borderRadius: 30,
    padding: 20,
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
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
    marginBottom: 40,
    paddingHorizontal: 40,
    maxWidth: 500
  },
  welcomeText: {
    fontSize: 28,
    fontWeight: '600',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  descriptionText: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    maxWidth: '80%'
  },
  buttonContainer: {
    width: '70%',
    gap: 15,
  },
  selectionButton: {
    backgroundColor: '#82CD7B',
    padding: 14,
    borderRadius: 25,
    alignItems: 'center',
    width: '100%',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 15,
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
  },
});