import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, View, Alert, ScrollView, TextInput } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import BackendManager from './auth/BackendManager';

export default function MentorApplicationScreen() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phoneNumber: '',
    country: '',
    stateProvince: '',
    schoolDistrict: '',
    timeZone: '',
    primarySubject: '',
    mentorSkills: ''
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async () => {
    try {
      // Send data to backend
      // const backendManager = BackendManager.getInstance();

      // const applicationData = {
      //   user_type: 'mentor',
      //   name: `${formData.firstName} ${formData.lastName}`,
      //   skills: formData.mentorSkills.split(',').map(skill => skill.trim()),
      //   experience: formData.primarySubject,
      //   availability: formData.timeZone,
      //   bio: `From ${formData.country}, ${formData.stateProvince}. Working in ${formData.schoolDistrict}.`
      // };

      // const result = await backendManager.submitApplication(applicationData);
      // console.log('Application submitted:', result);
      
      Alert.alert(
        "Success",
        "Your mentor profile has been saved successfully!",
        [
          {
            text: "Continue",
            onPress: () => router.replace('/(tabs)')
          }
        ]
      );
    } catch (error) {
      console.error('Profile submission failed:', error);
      Alert.alert("Error", "Failed to save your profile. Please try again.");
    }
  };

  return (
    <ThemedView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.card}>
            {/* Logo/Icon placeholder */}
            <View style={styles.logoContainer}>
              <View style={styles.logo} />
            </View>
          {/* Header */}
          <View style={styles.headerContainer}>
            <ThemedText style={styles.headerText}>
              We'd like to learn more about you.
            </ThemedText>
          </View>

          {/* Personal Information Section */}
          <View style={styles.sectionContainer}>
            <ThemedText style={styles.sectionTitle}>My Information</ThemedText>
            
            <View style={styles.rowContainer}>
              <View style={styles.halfInputContainer}>
                <ThemedText style={styles.inputLabel}>First Name</ThemedText>
                <TextInput 
                  style={styles.input}
                  value={formData.firstName}
                  onChangeText={(text) => handleChange('firstName', text)}
                />
              </View>
              
              <View style={styles.halfInputContainer}>
                <ThemedText style={styles.inputLabel}>Last Name</ThemedText>
                <TextInput 
                  style={styles.input}
                  value={formData.lastName}
                  onChangeText={(text) => handleChange('lastName', text)}
                />
              </View>
            </View>

            <View style={styles.inputContainer}>
              <ThemedText style={styles.inputLabel}>Phone Number</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.phoneNumber}
                onChangeText={(text) => handleChange('phoneNumber', text)}
                keyboardType="phone-pad"
              />
            </View>

            <View style={styles.inputContainer}>
              <ThemedText style={styles.inputLabel}>Country</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.country}
                onChangeText={(text) => handleChange('country', text)}
              />
            </View>

            <View style={styles.inputContainer}>
              <ThemedText style={styles.inputLabel}>State/Province</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.stateProvince}
                onChangeText={(text) => handleChange('stateProvince', text)}
              />
            </View>

            <View style={styles.inputContainer}>
              <ThemedText style={styles.inputLabel}>School District</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.schoolDistrict}
                onChangeText={(text) => handleChange('schoolDistrict', text)}
              />
            </View>

            <View style={styles.inputContainer}>
              <ThemedText style={styles.inputLabel}>Time Zone</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.timeZone}
                onChangeText={(text) => handleChange('timeZone', text)}
              />
            </View>
          </View>

          {/* Teaching Experience Section */}
          <View style={styles.sectionContainer}>
            <ThemedText style={styles.sectionTitle}>My Teaching Experience</ThemedText>
            
            <View style={styles.inputContainer}>
              <ThemedText style={styles.inputLabel}>Primary Subject Area(s) Taught</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.primarySubject}
                onChangeText={(text) => handleChange('primarySubject', text)}
              />
            </View>
            
            {/* New Skills Field */}
            <View style={styles.inputContainer}>
              <ThemedText style={styles.inputLabel}>Areas of Expertise</ThemedText>
              <ThemedText style={styles.inputDescription}>
                Share the specific skills, techniques, or knowledge areas where you can provide valuable guidance to mentees.
              </ThemedText>
              <TextInput 
                style={[styles.input, styles.multilineInput]}
                value={formData.mentorSkills}
                onChangeText={(text) => handleChange('mentorSkills', text)}
                multiline={true}
                numberOfLines={4}
                textAlignVertical="top"
                placeholder="Example: Classroom management, project-based learning, educational technology integration..."
                placeholderTextColor="#888"
              />
            </View>
          </View>

          {/* Submit Button */}
          <TouchableOpacity 
            style={styles.submitButton}
            onPress={handleSubmit}
          >
            <ThemedText style={styles.buttonText}>Submit</ThemedText>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingVertical: 20,
  },
  card: {
    backgroundColor: 'white',
    margin: 20,
    borderRadius: 30,
    padding: 20,
    flex: 1,
  },
  headerContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  headerText: {
    fontSize: 28,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
  sectionContainer: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '500',
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  rowContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  inputContainer: {
    marginBottom: 15,
    width: '100%',
  },
  halfInputContainer: {
    width: '48%',
    marginBottom: 15,
  },
  inputLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 5,
  },
  inputDescription: {
    fontSize: 14,
    color: '#888',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  input: {
    backgroundColor: '#f5f5f5',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  multilineInput: {
    minHeight: 100,
    paddingTop: 12,
  },
  submitButton: {
    backgroundColor: '#82CD7B',
    padding: 16,
    borderRadius: 25,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
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
});