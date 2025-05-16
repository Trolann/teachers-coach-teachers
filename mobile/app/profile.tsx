import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Image, SafeAreaView, StyleSheet, ScrollView, Platform } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import Header from '@/components/Header';
import BackendManager from './auth/BackendManager';
import { StatusBar } from 'expo-status-bar';
import { StatusBar as RNStatusBar } from 'react-native';

export default function ProfileScreen() {
  const [fullName, setFullName] = useState('');
  const [schoolDistrict, setSchoolDistrict] = useState('');
  const [subjectExpertise, setSubjectExpertise] = useState('');
  const [location, setLocation] = useState('');
  const [profileImage, setProfileImage] = useState(null);
  const backendManager = BackendManager.getInstance();
  const [credits, setCredits] = useState<number | null>(null);

  useEffect(() => {
    if (Platform.OS === 'ios') {
      RNStatusBar.setBackgroundColor('#ffffff'); // force white
      RNStatusBar.setBarStyle('dark-content');   // dark icons
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const tokens = await backendManager.getAvailableCredits();
        setCredits(tokens);

        const name = await backendManager.getUserName();
        console.log('Fetched name:', name);
        setFullName(name || '');

        // const picture = await backendManager.getPicture();
        // setProfileImage(picture || null);

        const district = await backendManager.getApplication();
        console.log('Fetched district:', district);


      } catch (error) {
        console.error('Error fetching credits:', error);
      }
    };

    fetchData();
  }
    , []);


  const handleImagePick = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 1,
    });

    if (!result.canceled) {
      setProfileImage(result.assets[0].uri);
    }
  };

  const handleSave = async () => {
    console.log('Saving Profile:', { fullName, schoolDistrict, subjectExpertise, location, profileImage });

    try {
      const [firstName, ...rest] = fullName.trim().split(' ');
      const lastName = rest.join(' ') || '';

      let uploadedImageUrl = null;

      if (profileImage && !profileImage.startsWith('http')) {
        console.log('Uploading image:', profileImage);
        const uploadResult = await backendManager.submitPicture(profileImage);
        console.log('Upload result:', uploadResult);

        if (uploadResult?.url) {
          uploadedImageUrl = uploadResult.url;
        } else {
          throw new Error('Image upload failed or returned no URL');
        }
      }

      const updateData = {
        firstName,
        lastName,
        school_district: schoolDistrict,
        subject_expertise: subjectExpertise,
        location: location,
        ...(uploadedImageUrl && { profile_image: uploadedImageUrl }),
      };

      const result = await backendManager.updateApplication(updateData);
      console.log('✅ Profile successfully updated:', result);
      alert('Profile updated! 🎉');
    } catch (error) {
      console.error('❌ Error saving profile:', error);
      alert('Oops! Couldn’t save profile. Try again later.');
    }
  };


  return (
    <View style={styles.safeArea}>
      <StatusBar style="dark" backgroundColor="white" />
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={{ paddingHorizontal: 20 }}>
          <Header subtitle="Edit Your Profile" />
        </View>

        <View style={styles.container}>
          <View style={styles.imageContainer}>
            <TouchableOpacity onPress={handleImagePick}>
              {profileImage ? (
                <Image source={{ uri: profileImage }} style={styles.profileImage} />
              ) : (
                <View style={styles.placeholderImage}>
                  <Text style={styles.placeholderText}>Add Photo</Text>
                </View>
              )}
            </TouchableOpacity>
            <View style={{ alignItems: 'center', marginTop: 10 }}>
              <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#005F99' }}>
                {credits ?? 0} 🪙
              </Text>
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Full Name</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your full name"
              value={fullName}
              onChangeText={setFullName}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>School District</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your school district"
              value={"East Side Union High School District"}
              onChangeText={setSchoolDistrict}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Subject Expertise</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. Math, Science, History"
              value={"Science"}
              onChangeText={setSubjectExpertise}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Location</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your city or state"
              value={"San Jose, CA"}
              onChangeText={setLocation}
            />
          </View>

          <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
            <Text style={styles.saveButtonText}>Save Profile</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    paddingTop: 65,
    backgroundColor: 'white',
  },
  scrollContainer: {
    paddingBottom: 40,
    backgroundColor: 'white',
  },
  container: {
    padding: 30,
    backgroundColor: 'white',
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  profileImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 2,
    borderColor: '#005F99',
  },
  placeholderImage: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#E0F2FF',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#005F99',
  },
  placeholderText: {
    color: '#005F99',
    fontSize: 14,
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 14,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#D1D5DB',
  },
  saveButton: {
    backgroundColor: '#28A745',
    paddingVertical: 14,
    borderRadius: 25,
    marginTop: 10,
    alignItems: 'center',
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});