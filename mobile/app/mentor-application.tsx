import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, View, Alert, ScrollView, TextInput, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
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
    mentorSkills: '',
  });

  const [selectedImage, setSelectedImage] = useState(null);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const pickImage = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permissionResult.granted) {
      Alert.alert("Permission denied", "Permission to access your media is required.");
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      const asset = result.assets[0];
      setSelectedImage(asset);
    }
  };

  const handleSubmit = async () => {
    try {
      const backendManager = BackendManager.getInstance();

      if (selectedImage) {
        await backendManager.submitPicture(selectedImage.uri);
      }

      Alert.alert("Success", "Your mentor profile has been saved successfully!", [
        {
          text: "Continue",
          onPress: async () => {
            try {
              const applicationStatus = await backendManager.getApplicationStatus();
              if (applicationStatus === 'approved') {
                router.replace('/mentor-approved');
              } else if (applicationStatus === 'denied') {
                router.replace('/mentor-denied');
              } else {
                router.replace('/mentor-waiting');
              }
            } catch (statusError) {
              console.error('Failed to fetch application status:', statusError);
              Alert.alert("Error", "Unable to check application status. Please try again later.");
            }
          },
        },
      ]);
    } catch (error) {
      console.error('Profile submission failed:', error);
      Alert.alert("Error", "Failed to save your profile. Please try again later.");
    }
  };

  return (
    <ThemedView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        {/* Logo */}
        <View style={styles.logoContainer}>
          <View style={styles.logo} />
        </View>

        {/* Header */}
        <View style={styles.headerContainer}>
          <ThemedText style={styles.headerText}>Become a Mentor</ThemedText>
          <ThemedText style={styles.subHeaderText}>
            Share your expertise and guide the next generation of educators.
          </ThemedText>
        </View>

        {/* Personal Information Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Personal Information</ThemedText>

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
          <ThemedText style={styles.sectionTitle}>Teaching Experience</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Primary Subject(s) Taught</ThemedText>
            <TextInput
              style={styles.input}
              value={formData.primarySubject}
              onChangeText={(text) => handleChange('primarySubject', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Areas of Expertise</ThemedText>
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

        {/* Image Picker */}
        <View style={{ alignItems: 'center', marginBottom: 20 }}>
          <TouchableOpacity onPress={pickImage}>
            {selectedImage ? (
              <Image
                source={{ uri: selectedImage.uri }}
                style={{ width: 100, height: 100, borderRadius: 50 }}
              />
            ) : (
              <View style={{ width: 100, height: 100, borderRadius: 50, backgroundColor: '#ccc', justifyContent: 'center', alignItems: 'center' }}>
                <ThemedText>Pick Image</ThemedText>
              </View>
            )}
          </TouchableOpacity>
        </View>

        {/* Submit Button */}
        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
          <ThemedText style={styles.buttonText}>Submit</ThemedText>
        </TouchableOpacity>
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    paddingTop: 50,
    backgroundColor: 'white',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingVertical: 20,
    paddingHorizontal: 15,
  },
  headerContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  headerText: {
    fontSize: 26,
    fontWeight: '600',
    color: 'black',
    textAlign: 'center',
  },
  sectionContainer: {
    marginBottom: 30,
  },
  subHeaderText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
    textAlign: 'center',
    marginTop: 10,
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
