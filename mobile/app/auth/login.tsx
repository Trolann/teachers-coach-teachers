// app/auth/login.tsx
import React, { useState } from 'react';
import { StyleSheet, TextInput, TouchableOpacity, View, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import { Ionicons } from '@expo/vector-icons';
import TokenManager from './TokenManager';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const handleLogin = async () => {
    try {
      const success = await TokenManager.getInstance().loginWithCredentials(email, password);
      console.error('Login status:', success);
      if (success) {
        router.replace('/pre-application');
      } else {
        Alert.alert('invalid credentials');
      }
    } catch (error) {
      console.error('Login failed:', error);
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
            <ThemedText style={styles.welcomeBack}>Welcome Back!</ThemedText>
            <ThemedText style={styles.pleaseLogin}>Please log in.</ThemedText>
          </View>

          {/* Input Fields */}
          <View style={styles.inputContainer}>
            <View style={styles.inputWrapper}>
              <Ionicons name="person-outline" size={20} color="#848282" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Enter your email"
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
                placeholder="Enter your password"
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

          {/* Login Button */}
          <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
            <ThemedText style={styles.loginButtonText}>Log In</ThemedText>
          </TouchableOpacity>

          {/* Divider */}
          <View style={styles.dividerContainer}>
            <View style={styles.divider} />
            <ThemedText style={styles.dividerText}>or</ThemedText>
            <View style={styles.divider} />
          </View>

          {/* Sign Up Button */}
          <TouchableOpacity
            style={styles.signUpButton}
            onPress={() => router.push('/auth/signup')}
          >
            <ThemedText style={styles.signUpButtonText}>Sign Up</ThemedText>
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
  welcomeBack: {
    fontSize: 28,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  pleaseLogin: {
    fontSize: 20,
    color: '#848282',
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
    color: '#333',
    paddingVertical: 8,
  },
  loginButton: {
    backgroundColor: '#48B2EE',
    padding: 16,
    borderRadius: 25,
    alignItems: 'center',
    marginBottom: 15,
    width: '85%',
  },
  loginButtonText: {
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
  signUpButton: {
    backgroundColor: '#48B2EE99',
    padding: 16,
    borderRadius: 25,
    alignItems: 'center',
    width: '85%',
  },
  signUpButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});