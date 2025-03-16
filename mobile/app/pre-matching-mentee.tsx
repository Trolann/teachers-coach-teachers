import React, { useState } from 'react';
import { 
  View, Text, TextInput, TouchableOpacity, Image, 
  StyleSheet, SafeAreaView, ScrollView 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

export default function FindMentorScreen() {
  const [goal, setGoal] = useState('');
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedIssues, setSelectedIssues] = useState([]);
  const router = useRouter();

  const categories = [
    "Nearby", 
    "Top Rated", 
    "Similar Expertise", 
    "Highly Experienced", 
    "Language-Specific Mentors",
    "Women Mentors", 
    "LGBTQ+ Friendly",
    "Veteran Mentors", 
    "Immigrant Mentors", 
    "Faith-Based Mentors", 
  ];

  const issues = [
    "Teaching concepts", "Time management", "Lack of motivation",
    "Preparing for an exam", "Career guidance", "Improving teaching habits",
    "Project assistance", "Technical skills", "Work-life balance"
  ];

  const toggleSelection = (item, list, setList, maxSelections) => {
    setList(prevList => {
      if (prevList.includes(item)) {
        return prevList.filter(i => i !== item);
      } else if (prevList.length < maxSelections) {
        return [...prevList, item];
      }
      return prevList;
    });
  };

  const handleFindMentor = () => {
    const requestData = { selectedCategories, selectedIssues, goal };
    console.log("Mentor Matching Data:", JSON.stringify(requestData, null, 2));
    router.push('/mentee-matching');
  };


  const renderOption = (item, list, setList, maxSelections, type) => {
    const backgroundColor = type === "categories" ? "#E6F9E6" : "#FDEDED"; 
    const selectedColor = type === "categories" ? "#4CAF50" : "#E53935"; 

    return (
      <TouchableOpacity
        key={item}
        style={[styles.optionButton, { backgroundColor }, list.includes(item) && { backgroundColor: selectedColor }]}
        onPress={() => toggleSelection(item, list, setList, maxSelections)}
      >
        <Text style={[styles.optionText, list.includes(item) && styles.selectedOptionText]}>
          {item}
        </Text>
      </TouchableOpacity>
    );
  };

  const renderIndependentScroll = (data, selectedList, setList, maxSelections, type) => {
    const firstRow = data.slice(0, Math.ceil(data.length / 2));
    const secondRow = data.slice(Math.ceil(data.length / 2));

    return (
      <>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalScroll}>
          {firstRow.map(item => renderOption(item, selectedList, setList, maxSelections, type))}
        </ScrollView>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalScroll}>
          {secondRow.map(item => renderOption(item, selectedList, setList, maxSelections, type))}
        </ScrollView>
      </>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.header}>
            <View style={styles.headerTextContainer}>
              <Text style={styles.greeting}>
                Hi, Jessica <Text style={styles.wave}>👋</Text>
              </Text>
              <Text style={styles.subtitle}>Find Your Perfect Mentor</Text>
            </View>
            <Image source={require('../assets/images/stock_pfp.jpeg')} style={styles.profileImage} />
          </View>
          <View style={styles.formContainer}>
            <View style={styles.mentorContainer}>
              <Text style={styles.title}>Find a Mentor</Text>

              <Text style={styles.label}>1) Select up to 3 mentor categories</Text>
              {renderIndependentScroll(categories, selectedCategories, setSelectedCategories, 3, "categories")}

              <Text style={styles.label}>2) Select up to 3 issues you need help with</Text>
              {renderIndependentScroll(issues, selectedIssues, setSelectedIssues, 3, "issues")}

              <Text style={styles.label}>3) Describe Your Goal for This Session</Text>
              <TextInput
                style={styles.input}
                placeholder="Write here..."
                placeholderTextColor="#999"
                multiline
                value={goal}
                onChangeText={setGoal}
              />

              <TouchableOpacity style={styles.button} onPress={handleFindMentor}>
                <Text style={styles.buttonText}>Find a Mentor</Text>
                <Ionicons name="paper-plane-outline" size={20} color="white" style={styles.buttonIcon} />
              </TouchableOpacity>
            </View>
          </View>
      </ScrollView>

      <View style={styles.navbar}>
        <Ionicons name="home" size={28} color="gray" />
        <Ionicons name="time-outline" size={28} color="gray" />
        <Ionicons name="heart-outline" size={28} color="gray" />
        <Ionicons name="person-outline" size={28} color="gray" />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
  },
  content: {
    paddingHorizontal: 20, 
    justifyContent: 'center',
    paddingTop: 20,
  },
  header: {
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'space-between', 
    marginBottom: 25,
  },
  headerTextContainer: {
    flex: 1,  
    justifyContent: 'center',
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  wave: {
    fontSize: 28, 
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  profileImage: {
    width: 45,
    height: 45,
    borderRadius: 25,
  },
  mentorContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 22, 
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
    color: '#333',
  },
  label: {
    fontSize: 14, 
    fontWeight: '600',
    color: '#444',
    marginTop: 18,
    marginBottom: 18,
  },
  horizontalScroll: {
    flexDirection: 'row',
    paddingVertical: 6,
  },
  optionButton: {
    backgroundColor: '#EEF2FF',
    paddingVertical: 8, 
    paddingHorizontal: 12, 
    borderRadius: 30,
    marginHorizontal: 5,
    elevation: 2,
  },
  selectedOption: {
    backgroundColor: '#2B6EF8',
  },
  optionText: {
    color: '#333',
    fontSize: 13, 
    fontWeight: '500',
  },
  selectedOptionText: {
    color: 'white',
  },
  input: {
    height: 60, 
    borderColor: '#ddd',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    textAlignVertical: 'top',
    backgroundColor: '#fff',
    width: '100%',
    marginBottom: 10,
  },
  button: {
    flexDirection: 'row',
    backgroundColor: 'black',
    padding: 15, 
    borderRadius: 25, 
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    marginTop: 22,
    marginBottom: 15,
  },
  buttonText: {
    color: 'white',
    fontSize: 16, 
    fontWeight: '600',
  },
  buttonIcon: {
    marginLeft: 8,
    fontSize: 16, 
  },
  navbar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: 8,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderColor: '#ddd',
  },
  formContainer: {
    paddingTop: 21,
  },
});
