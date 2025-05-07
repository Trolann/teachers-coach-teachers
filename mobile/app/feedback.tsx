import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, TextInput, ScrollView, Image } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import Header from '@/components/Header';
import { Ionicons } from '@expo/vector-icons';
import MenteeCard from '@/components/MenteeCard';

export default function FeedbackScreen() {
  const router = useRouter();
  const { mentor: mentorString } = useLocalSearchParams();
  const mentor = mentorString ? JSON.parse(mentorString as string) : null;
  
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [skillsImproved, setSkillsImproved] = useState('');
  const [skillsToImprove, setSkillsToImprove] = useState('');
  const [appImprovements, setAppImprovements] = useState('');
  const [submitted, setSubmitted] = useState(false);


  const [infoVisible, setInfoVisible] = useState(null);

  const toggleInfo = (mentorId) => {
    setInfoVisible(infoVisible === mentorId ? null : mentorId);
  };

  const handleRating = (selectedRating) => {
    setRating(selectedRating);
  };

  const handleSubmit = () => {
    // Here you would typically send the feedback to your backend
    console.log('Submitting feedback:', { 
      mentorId: mentor?.id, 
      rating, 
      feedback,
      skillsImproved,
      skillsToImprove,
      appImprovements
    });
    
    // For now, just mark as submitted
    setSubmitted(true);
  };

  const handleFinish = () => {
    // Navigate back to mentee matching or dashboard
    router.push('/mentee-matching');
  };

  const handleAddToFavorites = () => {
    // Implementation for adding to favorites
    console.log('Added to favorites:', mentor?.name);
  };

  const handleNotInterested = () => {
    // Implementation for not interested
    console.log('Not interested in:', mentor?.name);
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
          <Text style={styles.headerTitle}>Session Feedback</Text>
          <Text style={styles.rateSessionText}>Rate your session with {mentor?.name || 'your mentor'}</Text>
        </View>
        
        {/* Mentor Card */}
        <View style={styles.mentorCardContainer}>
          {mentor?.image && (
            <MenteeCard
              mentor={mentor}
              infoVisible={undefined}
              toggleInfo={undefined}
            />
          )}
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
                size={30} 
                color={rating >= star ? "#FFD700" : "#CCCCCC"} 
              />
            </TouchableOpacity>
          ))}
        </View>
        <Text style={styles.selectRatingText}>Select a rating</Text>
        
        {/* Feedback Text Area */}
        <View style={styles.questionsContainer}>
          <View style={styles.feedbackContainer}>
            <Text style={styles.feedbackLabel}>Share your experience (optional)</Text>
            <TextInput
              style={styles.feedbackInput}
              multiline
              numberOfLines={5}
              placeholder="What went well? What could be improved?"
              value={feedback}
              onChangeText={setFeedback}
            />
          </View>
          
          {/* Skills Improved Text Area */}
          <View style={styles.feedbackContainer}>
            <Text style={styles.feedbackLabel}>What skills did you improve on in this call?</Text>
            <TextInput
              style={styles.feedbackInput}
              multiline
              numberOfLines={3}
              placeholder="e.g. Communication, Leadership, Technical skills"
              value={skillsImproved}
              onChangeText={setSkillsImproved}
            />
          </View>
          
          {/* Skills To Improve Text Area */}
          <View style={styles.feedbackContainer}>
            <Text style={styles.feedbackLabel}>What skills do you want to improve on in your next call?</Text>
            <TextInput
              style={styles.feedbackInput}
              multiline
              numberOfLines={3}
              placeholder="e.g. Public speaking, Time management, Technical skills"
              value={skillsToImprove}
              onChangeText={setSkillsToImprove}
            />
          </View>
          
          {/* App Improvements Text Area */}
          <View style={styles.feedbackContainer}>
            <Text style={styles.feedbackLabel}>Any suggestions to improve our app?</Text>
            <TextInput
              style={styles.feedbackInput}
              multiline
              numberOfLines={3}
              placeholder="Share your ideas to make our app better"
              value={appImprovements}
              onChangeText={setAppImprovements}
            />
          </View>
        
        
        {/* Favorite/Not Interested Buttons */}
        <View style={styles.actionButtonsContainer}>
          <TouchableOpacity 
            style={styles.favoriteButton} 
            onPress={handleAddToFavorites}
          >
            <Ionicons name="heart" size={16} color="#FF4D4F" />
            <Text style={styles.favoriteButtonText}>Add to Favorites</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.notInterestedButton} 
            onPress={handleNotInterested}
          >
            <Ionicons name="close-circle" size={16} color="#0077B6" />
            <Text style={styles.notInterestedButtonText}>Not Interested</Text>
          </TouchableOpacity>
        </View>
        
        {/* Submit Button */}
        <TouchableOpacity 
          style={[styles.submitButton, rating === 0 && styles.disabledButton]} 
          onPress={handleSubmit}
          disabled={rating === 0}
        >
          <Text style={styles.buttonText}>Submit Feedback</Text>
        </TouchableOpacity>
        
        {/* Skip Button - Now Centered */}
        <TouchableOpacity 
          style={styles.skipButton}
          onPress={handleFinish}
        >
          <Text style={styles.skipButtonText}>Skip</Text>
        </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: 'white',
  },
  scrollContainer: {
    flexGrow: 1,
    paddingBottom: 80,
  },
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  headerContainer: {
    paddingHorizontal: 20,
    paddingTop: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 30,
    fontWeight: '600',
    color: '#005F99',
    textAlign: 'center',
    marginBottom: 10,
  },
  rateSessionText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  mentorCardContainer: {
    paddingHorizontal: 20,
    alignItems: 'center',
    marginBottom: 20,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: 'white',
  },
  mentorCard: {
    width: '100%',
    height: 320,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: '#f0f0f0',
  },
  mentorImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  mentorCardOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  mentorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 5,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  mentorLocation: {
    fontSize: 14,
    color: '#ffffff',
    marginLeft: 4,
  },
  ratingContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 15,
  },
  starButton: {
    marginHorizontal: 5,
  },
  selectRatingText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  feedbackContainer: {
    width: '100%',
    paddingHorizontal: 20,
    marginBottom: 20,
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
    minHeight: 100,
  },
  actionButtonsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  favoriteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFEAEA',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 20,
    flex: 1,
    marginRight: 10,
  },
  favoriteButtonText: {
    marginLeft: 8,
    color: '#B22222',
    fontSize: 14,
  },
  notInterestedButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#E0F2FF',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 20,
    flex: 1,
    marginLeft: 10,
  },
  notInterestedButtonText: {
    marginLeft: 8,
    color: '#005F99',
    fontSize: 14,
  },
  submitButton: {
    backgroundColor: '#28A745',
    paddingVertical: 14,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginHorizontal: 20,
    marginBottom: 10,
  },
  disabledButton: {
    backgroundColor: '#28A745',
    opacity: 0.75,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
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
    textAlign: 'center',
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
    backgroundColor: '#3498db',
    paddingVertical: 14,
    paddingHorizontal: 30,
    borderRadius: 25,
    width: '80%',
  },
  navbarItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  questionsContainer: {
    paddingHorizontal: 20,
    marginBottom: 5,
  },
});