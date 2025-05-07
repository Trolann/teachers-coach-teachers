import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet, Modal, Pressable, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import BackendManager from '../app/auth/BackendManager';
import TokenManager from '../app/auth/TokenManager'; // Import TokenManager

export function Header(props: { subtitle: string }) {
  const [showNav, setShowNav] = useState(false);
  const [credits, setCredits] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [userName, setUserName] = useState<string | null>(null);
  const router = useRouter();
  const backendManager = BackendManager.getInstance();
  const tokenManager = TokenManager.getInstance();
  const [userRole, setUserRole] = useState<string | null>(null);

  useEffect(() => {
    const fetchUserRole = async () => {
      const role = await tokenManager.getUserRole();
      setUserRole(role);
    };

    fetchUserRole();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
  
        // Try fetching credits
        const availableCredits = await backendManager.getAvailableCredits();
        setCredits(availableCredits);
  
        // Fetch user name
        // const application = await backendManager.getApplication();
        const name = await backendManager.getUserName();
        setUserName(name || 'User');

      } catch (error: any) {
        console.error('Error fetching data:', error);
  
        // Check if token expired
        if (error?.message?.includes('token is expired')) {
          console.log('Token expired — redirecting to login');
          backendManager.clearUserCache();
          router.push('/auth/login');
        } else {
          setCredits(0); // Default credits on error
        }
      } finally {
        setLoading(false);
      }
    };
  
    fetchData();
  }, []);

  return (
    <>
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text style={styles.greeting}>
            Hi, {userName || backendManager.getCachedUserName()} <Text style={styles.wave}>👋</Text>
          </Text>
          <Text style={styles.subtitle}>{props.subtitle}</Text>
        </View>

        <TouchableOpacity style={styles.profileSection} onPress={() => setShowNav(true)}>
          <Image source={require('../assets/images/stock_pfp.jpeg')} style={styles.profileImage} />
          {loading ? (
            <ActivityIndicator size="small" color="#666" style={styles.tokenLoader} />
          ) : (
            <Text style={styles.tokenText}>{credits ?? 0} 🪙</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Modal for Nav Options */}
      <Modal
        animationType="fade"
        transparent={true}
        visible={showNav}
        onRequestClose={() => setShowNav(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setShowNav(false)}>
          <View style={styles.navContainer}>
            {/* <Text style={styles.navTitle}>Navigation</Text> */}

            {userRole === 'mentee' && (
              <>
                <TouchableOpacity onPress={() => { setShowNav(false); router.push('/mentee-matching'); }}>
                  <Text style={styles.navItem}>🤝  Matching</Text>
                </TouchableOpacity>
                
                <TouchableOpacity onPress={() => { setShowNav(false); router.push('/liked'); }}>
                  <Text style={styles.navItem}>❤️  Liked</Text>
                </TouchableOpacity>
              </>
            )}

            <TouchableOpacity onPress={() => { setShowNav(false); router.push('/profile'); }}>
              <Text style={styles.navItem}>👤  Profile</Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={() => { 
              setShowNav(false); 
              // Clear user cache on logout
              backendManager.clearUserCache();
              router.push('/auth/login'); 
            }}>
              <Text style={[styles.navItem, styles.logoutItem]}>🚪  Logout</Text>
            </TouchableOpacity>

          </View>
        </Pressable>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 5,
    marginBottom: 20,
  },
  headerText: {
    flexDirection: 'column',
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  wave: {
    fontSize: 30,
  },
  subtitle: {
    fontSize: 16,
    paddingTop: 5,
    color: '#666',
  },
  profileSection: {
    flexDirection: 'column',
    alignItems: 'center',
  },
  profileImage: {
    width: 45,
    height: 45,
    borderRadius: 25,
  },
  tokenText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginTop: 4,
    textAlign: 'center',
  },
  tokenLoader: {
    marginTop: 4,
    height: 14, // Match the height of tokenText
  },
  modalOverlay: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
  },
  navContainer: {
    backgroundColor: '#fff',
    padding: 20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  navTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 15,
  },
  navItem: {
    fontSize: 19,
    fontWeight: '600',
    paddingVertical: 12,
    color: '#000',
  },
  logoutItem: {
    color: 'black',  // Change this to a different color if you want
  },
});

export default Header;
