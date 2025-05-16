import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, View, Alert, ScrollView, TextInput, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedView } from '@/components/ThemedView';
import { ThemedText } from '@/components/ThemedText';
import BackendManager from './auth/BackendManager';
import { Image } from 'react-native';

export default function MentorApplicationScreen() {
  const router = useRouter();
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
    expertiseGradeLevels: '',
    
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
    
    // Professional Qualifications
    teachingCertifications: '',
    advancedDegrees: '',
    pdLeadershipExperience: '',
    pedagogicalExpertise: '',
    
    // Mentorship Experience
    previousMentoringExperience: '',
    numTeachersMentored: '',
    mentoringStyle: '',
    maxMentees: '',
    
    // Specializations
    classroomManagement: false,
    technologyIntegration: false,
    assessmentDataAnalysis: false,
    curriculumDevelopment: false,
    studentEngagement: false,
    differentiatedInstruction: false,
    crisisResponse: false,
    specialEducation: false,
    
    // Additional Specializations
    additionalSpecializations: '',
    
    // Availability
    availabilityFrequency: '',
    preferredContactMethod: '',
    
    // Mentorship Philosophy
    mentoringPhilosophy: '',
    successMetrics: '',
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCheckboxChange = (field) => {
    setFormData(prev => ({
      ...prev,
      [field]: !prev[field]
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
    if (!validateForm()) return;

    try {
    // Verify BackendManager exists and is initialized
    const backendManager = BackendManager.getInstance();
    console.log('BackendManager instance:', backendManager);
    
    if (!backendManager || typeof backendManager.submitApplication !== 'function') {
      console.error('BackendManager is not properly initialized or missing submitApplication method');
      Alert.alert("Error", "Backend service is not available. Please try again later.");
      return;
    }
    
    // Log the form data being submitted
    console.log('Submitting form data:', formData);
    
    // Call the unified submitApplication method with the form data
    await backendManager.submitApplication('MENTOR', formData);

    console.log('Mentor profile stored successfully');
    
    Alert.alert(
      "Success",
      "Your mentor profile has been saved successfully!",
      [{ text: "Continue", onPress: () => router.replace('/(tabs)') }]
    );
    } catch (error) {
      console.error('Profile submission failed:', error);
      Alert.alert("Error", error.message || "Failed to save your profile. Please try again.");
    }
  };

  // Helper function for text inputs with suggestions
  const renderTextInputWithHint = (field, label, placeholder = '', hint = '') => {
    return (
      <View style={styles.inputContainer}>
        <ThemedText style={styles.inputLabel}>{label}</ThemedText>
        {hint && (
          <ThemedText style={styles.inputDescription}>{hint}</ThemedText>
        )}
        <TextInput 
          style={styles.input}
          value={formData[field]}
          onChangeText={(text) => handleChange(field, text)}
          placeholder={placeholder}
        />
      </View>
    );
  };

  // Helper function for checkboxes
  const renderCheckbox = (field, label) => {
    return (
      <TouchableOpacity 
        style={styles.checkboxContainer} 
        onPress={() => handleCheckboxChange(field)}
      >
        <View style={[styles.checkbox, formData[field] ? styles.checkboxChecked : null]} />
        <ThemedText style={styles.checkboxLabel}>{label}</ThemedText>
      </TouchableOpacity>
    );
  };

  return (
    <ThemedView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
          
        {/* Logo/Icon */}
        <View style={styles.logoContainer}>
          <Image
            source={require('@/assets/images/logo.png')}
            style={styles.logo}
          />
      </View>

        {/* Header */}
        <View style={styles.headerContainer}>
          <ThemedText style={styles.headerText}>
          🍎 Become a Mentor
          </ThemedText>
          <ThemedText style={styles.subHeaderText}>
            Share your expertise and guide the next generation of educators.
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
              placeholder="e.g., EST, PST, GMT+1"
            />
          </View>
        </View>

        {/* Teaching Experience Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Teaching Experience 📕</ThemedText>
          
          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Primary Subject(s) Taught</ThemedText>
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
              placeholder="Public, Private, Charter, Magnet, Alternative, Other"
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

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Grade Levels of Expertise</ThemedText>
            <ThemedText style={styles.inputDescription}>
              In which grade levels do you feel most experienced and comfortable mentoring others?
            </ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.expertiseGradeLevels}
              onChangeText={(text) => handleChange('expertiseGradeLevels', text)}
              placeholder="e.g., K-2, 6-8, 9-12"
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
              placeholder="e.g., More than 50% Caucasian, Hispanic, Mixed..."
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Secondary Racial Demographic</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.secondaryDemographic}
              onChangeText={(text) => handleChange('secondaryDemographic', text)}
              placeholder="e.g., Less than 50% Caucasian, Hispanic, Asian..."
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Socioeconomic Demographic</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.socioeconomicDemographic}
              onChangeText={(text) => handleChange('socioeconomicDemographic', text)}
              placeholder="e.g., Mixed, Mostly disadvantaged, Mostly not disadvantaged..."
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Percentage of English Language Learners</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.ellPercentage}
              onChangeText={(text) => handleChange('ellPercentage', text)}
              placeholder="e.g., 0-24%, 25-50%, 51-75%, 75%+"
            />
          </View>
        </View>

        {/* Professional Qualifications Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Professional Qualifications 💼</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Current Teaching Certifications</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.teachingCertifications}
              onChangeText={(text) => handleChange('teachingCertifications', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Advanced Degrees or Specialized Training</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.advancedDegrees}
              onChangeText={(text) => handleChange('advancedDegrees', text)}
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Professional Development Leadership Experience</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.pdLeadershipExperience}
              onChangeText={(text) => handleChange('pdLeadershipExperience', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Areas of Pedagogical Expertise</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.pedagogicalExpertise}
              onChangeText={(text) => handleChange('pedagogicalExpertise', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>
        </View>

        {/* Mentorship Experience Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Mentorship Experience 👔</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Previous Mentoring Experience (Formal or Informal)</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.previousMentoringExperience}
              onChangeText={(text) => handleChange('previousMentoringExperience', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Number of Teachers Previously Mentored</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.numTeachersMentored}
              onChangeText={(text) => handleChange('numTeachersMentored', text)}
              keyboardType="numeric"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Preferred Mentoring Style/Approach</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.mentoringStyle}
              onChangeText={(text) => handleChange('mentoringStyle', text)}
              multiline={true}
              textAlignVertical="top"
              placeholder="e.g., Collaborative, coach-like, direct instruction, question-based"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Maximum Number of Mentees Willing to Support</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.maxMentees}
              onChangeText={(text) => handleChange('maxMentees', text)}
              placeholder="e.g., 1, 2, 3, 4, 5+"
              keyboardType="numeric"
            />
          </View>
        </View>

        {/* Specializations Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Areas of Specialization 👌</ThemedText>
          <ThemedText style={styles.inputDescription}>
            Please select all areas in which you have significant expertise and could mentor others:
          </ThemedText>

          {renderCheckbox('classroomManagement', 'Classroom Management Strategies')}
          {renderCheckbox('technologyIntegration', 'Technology Integration')}
          {renderCheckbox('assessmentDataAnalysis', 'Assessment and Data Analysis')}
          {renderCheckbox('curriculumDevelopment', 'Curriculum Development')}
          {renderCheckbox('studentEngagement', 'Student Engagement Techniques')}
          {renderCheckbox('differentiatedInstruction', 'Differentiated Instruction')}
          {renderCheckbox('crisisResponse', 'Crisis Response/Trauma-Informed Teaching')}
          {renderCheckbox('specialEducation', 'Special Education Integration')}
          
          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Additional Areas of Specialization</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.additionalSpecializations}
              onChangeText={(text) => handleChange('additionalSpecializations', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>
        </View>

        {/* Availability Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Availability ⌚</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Available Meeting Frequency</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.availabilityFrequency}
              onChangeText={(text) => handleChange('availabilityFrequency', text)}
              placeholder="e.g., Weekly, Bi-weekly, Monthly, As needed"
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Preferred Contact Method</ThemedText>
            <TextInput 
              style={styles.input}
              value={formData.preferredContactMethod}
              onChangeText={(text) => handleChange('preferredContactMethod', text)}
              placeholder="e.g., Video call, Phone call, Email, Text message, In-person"
            />
          </View>
        </View>

        {/* Mentorship Philosophy Section */}
        <View style={styles.sectionContainer}>
          <ThemedText style={styles.sectionTitle}>Mentorship Philosophy 🤔</ThemedText>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>Your Mentoring Philosophy</ThemedText>
            <ThemedText style={styles.inputDescription}>
              Please share your approach to mentoring other educators.
            </ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.mentoringPhilosophy}
              onChangeText={(text) => handleChange('mentoringPhilosophy', text)}
              multiline={true}
              textAlignVertical="top"
              placeholder="Share your beliefs about effective mentoring..."
            />
          </View>

          <View style={styles.inputContainer}>
            <ThemedText style={styles.inputLabel}>How You Measure Mentoring Success</ThemedText>
            <TextInput 
              style={[styles.input, styles.multilineInput]}
              value={formData.successMetrics}
              onChangeText={(text) => handleChange('successMetrics', text)}
              multiline={true}
              textAlignVertical="top"
            />
          </View>
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
    fontWeight: '500',
    textAlign: 'center',
    marginTop: 10,
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
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  checkbox: {
    width: 20,
    height: 20,
    borderWidth: 1,
    borderColor: '#555',
    borderRadius: 4,
    marginRight: 10,
  },
  checkboxChecked: {
    backgroundColor: '#82CD7B',
    borderColor: '#82CD7B',
  },
  checkboxLabel: {
    fontSize: 16,
    color: '#333',
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
