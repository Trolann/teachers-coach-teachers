import React, { useState } from 'react';
import { StyleSheet, TextInput, TouchableOpacity, View, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import { Ionicons } from '@expo/vector-icons';
import TokenManager from './TokenManager';

export default function SignupScreen() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const handleSignup = async () => {
    try {
      const success = await TokenManager.getInstance().signUp({
        username: email,
        password: password,
        email: email,
        given_name: name,
        family_name: " ", // Required by Cognito but we'll leave it blank for now
        name: name,
        locale: "en_US",
        phone_number: '',
      });
      console.error('Signup status:', success);

      if (success) {
        // TODO: Alerts are not working. Update flow after signup and login (error handling)
        Alert.alert(
          "Success",
          "Please check your email for verification code",
          [{ text: "OK", onPress: () => router.push('/auth/login') }]
        );
      } else {
        Alert.alert("Error", "Signup failed");
      }
    } catch (error) {
      console.error('Signup failed:', error);
      Alert.alert("Error", error instanceof Error ? error.message : "Signup failed");
    }
  };

  return (
    <ThemedView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <View style={styles.card}>
          {/* Logo/Icon placeholder */}
          <View style={styles.logoContainer}>
            <View style={styles.logo} />
          </View>

          {/* Welcome Text */}
          <View style={styles.welcomeContainer}>
            <ThemedText style={styles.hiThere}>Hi there!</ThemedText>
            <ThemedText style={styles.getStarted}>Let's get started.</ThemedText>
          </View>

          {/* Input Fields */}
          <View style={styles.inputContainer}>
            <View style={styles.inputWrapper}>
              <Ionicons name="person-outline" size={20} color="#848282" style={styles.inputIcon} />

              <TextInput
                style={styles.input}
                placeholder="Name"
                value={name}
                onChangeText={setName}
                autoCapitalize="words"
                placeholderTextColor="#848282"
              />
            </View>

            <View style={styles.inputWrapper}>
              <Ionicons name="mail-outline" size={20} color="#848282" style={styles.inputIcon} />

              <TextInput
                style={styles.input}
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                placeholderTextColor="#848282"
              />
            </View>

            <View style={styles.inputWrapper}>
              <Ionicons name="lock-closed-outline" size={20} color="#848282" style={styles.inputIcon} />

              <TextInput
                style={styles.input}
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                placeholderTextColor="#848282"
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <Ionicons 
                    name={showPassword ? "eye-outline" : "eye-off-outline"} 
                    size={20} 
                    color="#848282" 
                />
              </TouchableOpacity>
            </View>
          </View>

          {/* Sign Up Button */}
          <TouchableOpacity style={styles.signUpButton} onPress={handleSignup}>
            <ThemedText style={styles.signUpButtonText}>Sign Up</ThemedText>
          </TouchableOpacity>

          {/* Divider */}
          <View style={styles.dividerContainer}>
            <View style={styles.divider} />
            <ThemedText style={styles.dividerText}>or</ThemedText>
            <View style={styles.divider} />
          </View>

          {/* Login Button */}
          <TouchableOpacity 
            style={styles.loginButton}
            onPress={() => router.push('/auth/login')}
          >
            <ThemedText style={styles.loginButtonText}>Log In</ThemedText>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  keyboardView: {
    flex: 1,
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
    marginBottom: 20,
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
    marginBottom: 30,
  },
  hiThere: {
    // fontSize: 28,
    // fontWeight: '600',
    // color: '#2F2F2FBF',
    // marginBottom: 25,
    fontSize: 28,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  getStarted: {
    // fontSize: 30,
    // color: '#2F2F2F',
    // fontFamily: 'Inter',
    // fontWeight: '700',
    fontSize: 20,
    color: '#666',
  },
  
  inputContainer: {
    gap: 15,
    marginBottom: 20,
    width: '85%',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
    paddingBottom: 8,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#848282',
    paddingVertical: 8,
    fontFamily: 'Montserrat',
    fontWeight: '300',
  },
  signUpButton: {
    backgroundColor: '#48B2EE',
    padding: 16,
    borderRadius: 25,
    alignItems: 'center',
    marginBottom: 15,
    width: '85%',
  },
  signUpButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 15,
    width: '85%',
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
  loginButton: {
    backgroundColor: '#48B2EE99',
    padding: 16,
    borderRadius: 25,
    alignItems: 'center',
    width: '85%',
  },
  loginButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});
