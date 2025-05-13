import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, TextInput, ScrollView, Image, Alert } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import Header from '@/components/Header';
import { Ionicons } from '@expo/vector-icons';
import BackendManager from './auth/BackendManager';

export default function FeedbackScreen() {
  console.log('Rendering FeedbackScreen component');
  const router = useRouter();
  const { mentor: mentorString, sessionId } = useLocalSearchParams();
  console.log('Session ID from params:', sessionId);
  
  const mentor = mentorString ? JSON.parse(mentorString as string) : null;
  console.log('Mentor data parsed:', mentor ? `${mentor.name} (ID: ${mentor.id})` : 'No mentor data');
  
  const [sessionIdState, setSessionIdState] = useState(sessionId || null);
  const [rating, setRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [skillsImproved, setSkillsImproved] = useState('');
  const [skillsToImprove, setSkillsToImprove] = useState('');
  const [appImprovements, setAppImprovements] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Log when component mounts
  useEffect(() => {
    console.log('FeedbackScreen mounted with sessionId:', sessionId);
    return () => {
      console.log('FeedbackScreen unmounted');
    };
  }, []);

  // Create an instance of the BackendManager
  const backendManager = BackendManager.getInstance();
  console.log('BackendManager instance created');

  const handleRating = (selectedRating) => {
    console.log('Rating selected:', selectedRating);
    setRating(selectedRating);
  };

  const handleSubmit = async () => {
    console.log('Submit button pressed');
    setSubmitted(true);

    // TODO: pass sessionId correct (feedback infromation properly implemented)
    // if (!sessionId) {
    //   console.error('Submit failed: Missing sessionId');
    //   Alert.alert("Error", "Session ID is required to submit feedback.");
    //   return;
    // }
    
    // if (rating === 0) {
    //   console.warn('Submit validation: No rating provided');
    //   Alert.alert("Incomplete Feedback", "Please provide a rating before submitting.");
    //   return;
    // }
    
    // console.log('Starting feedback submission process');
    // setIsLoading(true);

    // try {
    //   // Prepare feedback data
    //   const feedbackData = {
    //     rating,
    //     feedback,
    //     skillsImproved,
    //     skillsToImprove,
    //     appImprovements
    //   };
      
    //   console.log('Feedback data to submit:', feedbackData);
      
    //   // Submit feedback to the backend
    //   console.log(`Calling backendManager.submitSessionFeedback for session: ${sessionId}`);
    //   const response = await backendManager.submitSessionFeedback(
    //     sessionId as string,
    //     feedbackData,
    //     false // This is mentee feedback
    //   );
      
    //   console.log('Feedback submission response:', response);
      
    //   // Update session status to completed
    //   console.log(`Updating session status to completed for session: ${sessionId}`);
    //   await backendManager.updateSessionStatus(sessionId as string, 'completed');
    //   console.log('Session status updated successfully');
      
    //   // For the favorites/not interested functionality
    //   if (mentor) {
    //     console.log('Mentor data available for favorites/not interested:', mentor.id);
    //   }
      
    //   console.log('Feedback submission successful, setting submitted state to true');
    //   setSubmitted(true);
    // } catch (error) {
    //   console.error('Error submitting feedback:', error);
    //   console.error('Error details:', error.message);
    //   Alert.alert(
    //     "Submission Failed",
    //     "There was an error submitting your feedback. Please try again."
    //   );
    // } finally {
    //   console.log('Feedback submission process completed, setting loading state to false');
    //   setIsLoading(false);
    // }
  };

  const handleFinish = () => {
    console.log('Finish button pressed, navigating to mentee-matching');
    router.push('/mentee-matching');
  };

  const handleAddToFavorites = async () => {
    console.log('Add to favorites button pressed');
    
    if (!mentor?.id) {
      console.error('Add to favorites failed: Missing mentor ID');
      Alert.alert("Error", "Mentor information is missing.");
      return;
    }
    
    try {
      // TODO Implementation for adding to favorites would go here with corresponding backend API endpoint
      console.log('Added mentor to favorites:', mentor.id, mentor.name);
      Alert.alert("Success", `${mentor?.name} added to favorites!`);
    } catch (error) {
      console.error('Error adding to favorites:', error);
      console.error('Error details:', error.message);
      Alert.alert("Error", "Failed to add mentor to favorites.");
    }
  };

  const handleNotInterested = async () => {
    console.log('Not interested button pressed');
    
    if (!mentor?.id) {
      console.error('Not interested failed: Missing mentor ID');
      Alert.alert("Error", "Mentor information is missing.");
      return;
    }
    
    try {
      // TODO: Implementation for not interested would go here need corresponding backend API endpoint
      console.log('Marked mentor as not interested:', mentor.id, mentor.name);
      Alert.alert("Success", `${mentor?.name} marked as not interested.`);
    } catch (error) {
      console.error('Error marking as not interested:', error);
      console.error('Error details:', error.message);
      Alert.alert("Error", "Failed to mark mentor as not interested.");
    }
  };

  console.log('Current state - submitted:', submitted, 'rating:', rating, 'isLoading:', isLoading);

  if (submitted) {
    console.log('Rendering thank you screen');
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

  console.log('Rendering main feedback form');
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
            <View style={styles.mentorCard}>
              <Image 
                source={typeof mentor.image === 'string' ? { uri: mentor.image } : mentor.image} 
                style={styles.mentorImage} 
                onLoad={() => console.log('Mentor image loaded successfully')}
                onError={(error) => console.error('Error loading mentor image:', error.nativeEvent.error)}
              />
              <View style={styles.mentorCardOverlay}>
                <Text style={styles.mentorName}>{mentor?.name || 'Mentor Name'}</Text>
                <View style={styles.locationContainer}>
                  <Ionicons name="location-outline" size={14} color="#ffffff" />
                  <Text style={styles.mentorLocation}>{mentor?.location || 'Location'}</Text>
                </View>
              </View>
            </View>
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
        <View style={styles.feedbackContainer}>
          <Text style={styles.feedbackLabel}>Share your experience</Text>
          <TextInput
            style={styles.feedbackInput}
            multiline
            numberOfLines={5}
            placeholder="What went well? What could be improved?"
            value={feedback}
            onChangeText={(text) => {
              console.log('Experience feedback updated');
              setFeedback(text);
            }}
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
            onChangeText={(text) => {
              console.log('Skills improved updated');
              setSkillsImproved(text);
            }}
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
            onChangeText={(text) => {
              console.log('Skills to improve updated');
              setSkillsToImprove(text);
            }}
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
            onChangeText={(text) => {
              console.log('App improvements updated');
              setAppImprovements(text);
            }}
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
            <Ionicons name="close-circle" size={16} color="#666" />
            <Text style={styles.notInterestedButtonText}>Not Interested</Text>
          </TouchableOpacity>
        </View>
        
        {/* Submit Button */}
        <TouchableOpacity 
          style={[
            styles.submitButton, 
            (rating === 0 || isLoading) && styles.disabledButton
          ]} 
          onPress={handleSubmit}
          disabled={rating === 0 || isLoading}
        >
          <Text style={styles.buttonText}>
            {isLoading ? "Submitting..." : "Submit Feedback"}
          </Text>
        </TouchableOpacity>
       
        {/* Skip Button - Now Centered */}
        <TouchableOpacity 
          style={styles.skipButton}
          onPress={handleFinish}
          disabled={isLoading}
        >
          <Text style={styles.skipButtonText}>Skip</Text>
        </TouchableOpacity>
      </ScrollView>
      
      {/* Bottom Navigation Bar */}
      <View style={styles.bottomNavbar}>
        <TouchableOpacity 
          style={styles.navbarItem}
          onPress={() => {
            console.log('Home navigation button pressed');
            // Add navigation logic here
          }}
        >
          <Ionicons name="home" size={24} color="#000" />
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.navbarItem}
          onPress={() => {
            console.log('Time navigation button pressed');
            // Add navigation logic here
          }}
        >
          <Ionicons name="time" size={24} color="#666" />
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.navbarItem}
          onPress={() => {
            console.log('Heart navigation button pressed');
            // Add navigation logic here
          }}
        >
          <Ionicons name="heart" size={24} color="#666" />
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.navbarItem}
          onPress={() => {
            console.log('Profile navigation button pressed');
            // Add navigation logic here
          }}
        >
          <Ionicons name="person" size={24} color="#666" />
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#ffffff',
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
    fontSize: 22,
    fontWeight: '600',
    color: '#333',
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
    padding: 16,
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
    marginVertical: 10,
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
    marginBottom: 30,
  },
  favoriteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f0f0f0',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 20,
    flex: 1,
    marginRight: 10,
  },
  favoriteButtonText: {
    marginLeft: 8,
    color: '#333',
    fontSize: 14,
  },
  notInterestedButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f0f0f0',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 20,
    flex: 1,
    marginLeft: 10,
  },
  notInterestedButtonText: {
    marginLeft: 8,
    color: '#333',
    fontSize: 14,
  },
  submitButton: {
    backgroundColor: '#00c851',
    paddingVertical: 14,
    paddingHorizontal: 30,
    borderRadius: 25,
    marginHorizontal: 20,
    marginBottom: 15,
  },
  disabledButton: {
    backgroundColor: '#a0a0a0',
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
    marginBottom: 20,
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
  bottomNavbar: {
    flexDirection: 'row',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 60,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  navbarItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
});