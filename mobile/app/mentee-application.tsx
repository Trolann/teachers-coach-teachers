import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, View, Alert, ScrollView, TextInput, Platform, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import BackendManager from './auth/BackendManager';
import { Image } from 'react-native';

export default function MenteeApplicationScreen() {
  const router = useRouter();
  const [selectedImage, setSelectedImage] = useState(null);
  
  const [formData, setFormData] = useState({
    // Personal Information
    firstName: '',
    lastName: '',
    phoneNumber: '',
    
    // Geographic Information
    country: '',
    stateProvince: '',
    county: '',
    schoolDistrict: '',
    timeZone: '',
    
    // Teaching Experience
    primarySubject: '',
    educationCertifications: '',
    specializedPrograms: '',
    schoolType: '',
    currentGradeLevels: '',
    previousGradeLevels: '',
    
    // Years of Experience
    yearsInEducation: '',
    yearsInCurrentRole: '',
    yearsInCurrentGradeLevel: '',
    yearsInCurrentSubject: '',
    
    // Student Demographics
    racialDemographic: '',
    secondaryDemographic: '',
    socioeconomicDemographic: '',
    ellPercentage: '',
    
    // Community Context
    schoolSocioeconomicDesignation: '',
    freeReducedLunchPercentage: '',
    primaryLanguages: '',
    majorIndustries: '',
    studentBarriers: '',
    householdIncomeRange: '',
    housingInsecurityPercentage: '',
    technologyAccess: '',
    
    // Mentorship Goals
    supportAreas: '',
    immediateChallenges: '',
    mentorshipGoals: '',
    improvementTimeline: '',
    sessionFrequency: '',
    desiredMentorCharacteristics: '',
    
    // Professional Goals
    shortTermGoals: '',
    longTermGoals: '',
    professionalGrowthAreas: '',
    skillsToDevelop: '',
    
    // Current Resources
    currentSupportSystems: '',
    previousMentorship: '',
    professionalDevelopmentAccess: '',
    districtConstraints: '',

    selectedCategories: [],
    selectedIssues: [],
    goal: '',
  });

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

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = () => {
      // Check required fields
      if (!formData.firstName || !formData.lastName) {
        Alert.alert("Error", "Please enter your first and last name.");
        return false;
      }
          
      return true;
    };

  const handleSubmit = async () => {
    if(!validateForm()) return;

    try {
      // Verify BackendManager exists and is initialized
      const backendManager = BackendManager.getInstance();
      console.log('BackendManager instance:', backendManager);

      // Upload image if selected
      if (selectedImage) {
        await backendManager.submitPicture(selectedImage.uri);
      }
      
      if (!backendManager || typeof backendManager.submitApplication !== 'function') {
        console.error('BackendManager is not properly initialized or missing submitApplication method');
        Alert.alert("Error", "Backend service is not available. Please try again later.");
        return;
      }
      
      // Log the form data being submitted
      console.log('Submitting form data:', formData);
      
      // Call the unified submitApplication method with the form data
      await backendManager.submitApplication('MENTEE', formData);

      console.log('Mentee profile stored successfully');
      
      Alert.alert(
        "Success",
        "Your mentee profile has been saved successfully!",
        [{ text: "Continue", onPress: () => router.replace('/(tabs)') }]
      );
    } catch (error) {
      console.error('Profile submission failed:', error);
      Alert.alert("Error", "Failed to save your profile. Please try again.");
    }
  };

  return (
    <ThemedView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer} style={{ borderWidth: 0, shadowOpacity: 0 }}>
      <View style={styles.logoContainer}>
      <Image
        source={require('@/assets/images/logo.png')}
        style={styles.logo}
      />
    </View>

        
        {/* Header */}
        <View style={styles.headerContainer}>
          <ThemedText style={styles.headerText}>
          ✏️ Mentee Application
          </ThemedText>
          <ThemedText style={styles.subHeaderText}>
            Tell us about yourself, your teaching context, and what you're looking for in a mentor.
          </ThemedText>
        </View>

        {/* Personal Information Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Personal Information 📝</ThemedText>
          
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
        </View>

        {/* Geographic Information Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Geographic Information 🗺️</ThemedText>

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
            <ThemedText style={styles.inputLabel}>County</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.county}
              onChangeText={(text) => handleChange('county', text)}
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
          <ThemedText style={styles.sectionTitle}>Teaching Experience 📕</ThemedText>
          
          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Primary Subject Area(s) Taught</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.primarySubject}
              onChangeText={(text) => handleChange('primarySubject', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Education Certifications</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.educationCertifications}
              onChangeText={(text) => handleChange('educationCertifications', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Specialized Programs (e.g., AP, STEM)</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.specializedPrograms}
              onChangeText={(text) => handleChange('specializedPrograms', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>School Type</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.schoolType}
              onChangeText={(text) => handleChange('schoolType', text)}
              placeholder="Public, Private, Charter, Magnet, Alternative, etc."
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Current Grade Levels</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.currentGradeLevels}
              onChangeText={(text) => handleChange('currentGradeLevels', text)}
              placeholder="e.g., 4-5, 9-12, K-3"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Previous Grade Level Experience</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.previousGradeLevels}
              onChangeText={(text) => handleChange('previousGradeLevels', text)}
            />
          </View>
        </View>

        {/* Years of Experience Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Years of Experience 📆</ThemedText>

          <View style={styles.rowContainer}>
            <View style={styles.halfInputContainer}>
              <ThemedText style={styles.inputLabel}>Years in Education</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.yearsInEducation}
                onChangeText={(text) => handleChange('yearsInEducation', text)}
                keyboardType="numeric"
              />
            </View>
            
            <View style={styles.halfInputContainer}>
              <ThemedText style={styles.inputLabel}>Years in Current Role</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.yearsInCurrentRole}
                onChangeText={(text) => handleChange('yearsInCurrentRole', text)}
                keyboardType="numeric"
              />
            </View>
          </View>

          <View style={styles.rowContainer}>
            <View style={styles.halfInputContainer}>
              <ThemedText style={styles.inputLabel}>Years in Current Grade Level</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.yearsInCurrentGradeLevel}
                onChangeText={(text) => handleChange('yearsInCurrentGradeLevel', text)}
                keyboardType="numeric"
              />
            </View>
            
            <View style={styles.halfInputContainer}>
              <ThemedText style={styles.inputLabel}>Years in Current Subject</ThemedText>
              <TextInput 
                style={styles.input}
                value={formData.yearsInCurrentSubject}
                onChangeText={(text) => handleChange('yearsInCurrentSubject', text)}
                keyboardType="numeric"
              />
            </View>
          </View>
        </View>

        {/* Student Demographics Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Student Demographics 📚</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Primary Racial Demographic</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.racialDemographic}
              onChangeText={(text) => handleChange('racialDemographic', text)}
              placeholder="e.g., More than 50% Caucasian, More than 50% Hispanic, etc."
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Secondary Racial Demographic</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.secondaryDemographic}
              onChangeText={(text) => handleChange('secondaryDemographic', text)}
              placeholder="e.g., Less than 50% Asian, Less than 50% African American, etc."
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Socioeconomic Demographic</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.socioeconomicDemographic}
              onChangeText={(text) => handleChange('socioeconomicDemographic', text)}
              placeholder="e.g., More than 50% socioeconomically disadvantaged"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Percentage of English Language Learners</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.ellPercentage}
              onChangeText={(text) => handleChange('ellPercentage', text)}
              placeholder="e.g., 0-24%, 25-50%, 51-75%, 75% and higher"
            />
          </View>
        </View>

        {/* Community Context Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Community Context 👥</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>School's Socioeconomic Designation (e.g., Title I)</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.schoolSocioeconomicDesignation}
              onChangeText={(text) => handleChange('schoolSocioeconomicDesignation', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>% Students Qualifying for Free/Reduced Lunch</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.freeReducedLunchPercentage}
              onChangeText={(text) => handleChange('freeReducedLunchPercentage', text)}
              keyboardType="numeric"
              placeholder="e.g., 45"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Primary Languages Spoken in Community</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.primaryLanguages}
              onChangeText={(text) => handleChange('primaryLanguages', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Major Industries/Employers in Community</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.majorIndustries}
              onChangeText={(text) => handleChange('majorIndustries', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Common Barriers to Student Success</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.studentBarriers}
              onChangeText={(text) => handleChange('studentBarriers', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Average Household Income Range</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.householdIncomeRange}
              onChangeText={(text) => handleChange('householdIncomeRange', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>% Students with Housing Insecurity</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.housingInsecurityPercentage}
              onChangeText={(text) => handleChange('housingInsecurityPercentage', text)}
              keyboardType="numeric"
              placeholder="e.g., 15"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Student Technology Access</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.technologyAccess}
              onChangeText={(text) => handleChange('technologyAccess', text)}
              placeholder="e.g., 1:1 devices with home internet, Shared devices, etc."
            />
          </View>
        </View>

        {/* Mentorship Goals Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Mentorship Goals 💪🏼</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Areas Seeking Support</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.supportAreas}
              onChangeText={(text) => handleChange('supportAreas', text)}
              multiline={true}
              textAlignVertical="top"
              placeholder="e.g., Classroom management, technology integration, student engagement"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Immediate Challenges or Concerns</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.immediateChallenges}
              onChangeText={(text) => handleChange('immediateChallenges', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Specific Goals for Mentorship</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.mentorshipGoals}
              onChangeText={(text) => handleChange('mentorshipGoals', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Timeline for Desired Improvements</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.improvementTimeline}
              onChangeText={(text) => handleChange('improvementTimeline', text)}
              placeholder="e.g., Immediate (1-3 months), Short-term (3-6 months), etc."
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Desired Frequency of Sessions</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.sessionFrequency}
              onChangeText={(text) => handleChange('sessionFrequency', text)}
              placeholder="e.g., Weekly, Bi-weekly, Monthly, As needed"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Desired Mentor Characteristics</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.desiredMentorCharacteristics}
              onChangeText={(text) => handleChange('desiredMentorCharacteristics', text)}
              multiline={true}
              textAlignVertical="top"
              placeholder="e.g., Experience with similar demographics, expertise in specific teaching methods"
            />
          </View>
        </View>

        {/* Professional Goals Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Professional Goals 🏅</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Short-term Teaching Goals</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.shortTermGoals}
              onChangeText={(text) => handleChange('shortTermGoals', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Long-term Career Objectives</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.longTermGoals}
              onChangeText={(text) => handleChange('longTermGoals', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Areas for Professional Growth</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.professionalGrowthAreas}
              onChangeText={(text) => handleChange('professionalGrowthAreas', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Specific Skills to Develop</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.skillsToDevelop}
              onChangeText={(text) => handleChange('skillsToDevelop', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>
        </View>

        {/* Current Resources Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Current Resources 🌐</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Current Support Systems Available</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.currentSupportSystems}
              onChangeText={(text) => handleChange('currentSupportSystems', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Previous Mentorship Experience</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.previousMentorship}
              onChangeText={(text) => handleChange('previousMentorship', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Access to Professional Development</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.professionalDevelopmentAccess}
              onChangeText={(text) => handleChange('professionalDevelopmentAccess', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>District/School Constraints or Requirements</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.districtConstraints}
              onChangeText={(text) => handleChange('districtConstraints', text)}
              multiline={true}
              textAlignVertical="top"
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
        <TouchableOpacity 
          style={styles.submitButton}
          onPress={handleSubmit}
        >
          <ThemedText style={styles.buttonText}>Submit Application</ThemedText>
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
  subHeaderText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '400',
    textAlign: 'center',
    marginTop: 8,
  },
  sectionContainer: {
    marginBottom: 30,
    paddingVertical: 15,
    backgroundColor: '#f9f9f9',
    borderRadius: 10,
    paddingHorizontal: 15,
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
    color: '#444',
    marginBottom: 5,
    fontWeight: '500',
  },
  inputDescription: {
    fontSize: 14,
    color: '#888',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  input: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  multilineInput: {
    minHeight: 100,
    paddingTop: 12,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: '#82CD7B',
    padding: 16,
    borderRadius: 25,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 40,
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
