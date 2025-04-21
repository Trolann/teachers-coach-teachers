import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, TextInput, ScrollView } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import Header from '@/components/Header';
import { Ionicons } from '@expo/vector-icons';

export default function FeedbackScreen() {
  const router = useRouter();
  const { mentor: mentorString } = useLocalSearchParams();
  const mentor = mentorString ? JSON.parse(mentorString as string) : null;
  
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleRating = (selectedRating) => {
    setRating(selectedRating);
  };

  const handleSubmit = () => {
    // Here you would typically send the feedback to your backend
    console.log('Submitting feedback:', { mentorId: mentor?.id, rating, feedback });
    
    // For now, just mark as submitted
    setSubmitted(true);
  };

  const handleFinish = () => {
    // Navigate back to mentee matching or dashboard
    router.push('/mentee-matching');
  };

  if (submitted) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.container}>
          <Text style={styles.thankYouTitle}>Thank You!</Text>
          <Text style={styles.thankYouText}>Your feedback has been submitted.</Text>
          <View style={styles.iconContainer}>
            <Ionicons name="checkmark-circle" size={80} color="#00c851" />
          </View>
          <TouchableOpacity style={styles.finishButton} onPress={handleFinish}>
            <Text style={styles.buttonText}>Return to Home</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.headerContainer}>
          <Header subtitle="Session Feedback" />
        </View>
        
        <View style={styles.mentorInfoContainer}>
          <Text style={styles.mentorTitle}>How was your session with</Text>
          <Text style={styles.mentorName}>{mentor?.name || 'your mentor'}?</Text>
        </View>
        
        {/* Rating Stars */}
        <View style={styles.ratingContainer}>
          {[1, 2, 3, 4, 5].map((star) => (
            <TouchableOpacity 
              key={star} 
              onPress={() => handleRating(star)}
              style={styles.starButton}
            >
              <Ionicons 
                name={rating >= star ? "star" : "star-outline"} 
                size={40} 
                color={rating >= star ? "#FFD700" : "#BBBBBB"} 
              />
            </TouchableOpacity>
          ))}
        </View>
        
        {/* Feedback Text Area */}
        <View style={styles.feedbackContainer}>
          <Text style={styles.feedbackLabel}>Additional Comments (Optional)</Text>
          <TextInput
            style={styles.feedbackInput}
            multiline
            numberOfLines={5}
            placeholder="Tell us more about your experience..."
            value={feedback}
            onChangeText={setFeedback}
          />
        </View>
        
        {/* Submit Button */}
        <TouchableOpacity 
          style={[styles.submitButton, rating === 0 && styles.disabledButton]} 
          onPress={handleSubmit}
          disabled={rating === 0}
        >
          <Text style={styles.buttonText}>Submit Feedback</Text>
        </TouchableOpacity>
        
        {/* Skip Button */}
        <TouchableOpacity 
          style={styles.skipButton}
          onPress={handleFinish}
        >
          <Text style={styles.skipButtonText}>Skip</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f7f7f7',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingBottom: 30,
  },
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  headerContainer: {
    paddingHorizontal: 20,
    paddingTop: 65,
  },
  mentorInfoContainer: {
    alignItems: 'center',
    marginTop: 30,
    marginBottom: 20,
  },
  mentorTitle: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
  },
  mentorName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginTop: 5,
  },
  ratingContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginVertical: 30,
  },
  starButton: {
    marginHorizontal: 8,
  },
  feedbackContainer: {
    width: '100%',
    paddingHorizontal: 20,
    marginBottom: 30,
  },
  feedbackLabel: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 10,
    color: '#333',
  },
  feedbackInput: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 15,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: '#ddd',
    fontSize: 16,
    minHeight: 120,
  },
  submitButton: {
    backgroundColor: '#00c851',
    paddingVertical: 14,
    paddingHorizontal: 30,
    borderRadius: 10,
    alignSelf: 'center',
    marginBottom: 15,
    width: '80%',
  },
  disabledButton: {
    backgroundColor: '#aaaaaa',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
  skipButton: {
    paddingVertical: 10,
    alignSelf: 'center',
  },
  skipButtonText: {
    color: '#666',
    fontSize: 16,
  },
  thankYouTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  thankYouText: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  iconContainer: {
    marginBottom: 40,
  },
  finishButton: {
    backgroundColor: '#00c851',
    paddingVertical: 14,
    paddingHorizontal: 30,
    borderRadius: 10,
    width: '80%',
  },
});