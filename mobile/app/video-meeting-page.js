import React, { useRef, useState } from 'react';
import {
    View,
    StyleSheet,
    Image,
    Text,
    TouchableOpacity,
} from 'react-native';
import {
    ZegoUIKitPrebuiltCall,
    ONE_ON_ONE_VIDEO_CALL_CONFIG,
    ZegoMenuBarButtonName,
    ZegoUIKitPrebuiltCallService,
} from '@zegocloud/zego-uikit-prebuilt-call-rn';
import {
    CameraView,
    CameraType,
    useCameraPermissions,
} from 'expo-camera';
import pfp from '../assets/images/stock_pfp.jpeg';

export default function VoiceCallPage({ navigation }) {
    const prebuiltRef = useRef();
    const [facing, setFacing] = useState('front');
    const [permission, requestPermission] = useCameraPermissions();

    const appID = 1744857505;
    const appSign =
        'd67d732b8bc0a309a1e40b09d8a570bad9c94841486d81b3ebae940098cb195a';
    const userID = '60791697';
    const userName = userID;
    const callID = 'testCall_01';

    const toggleCameraFacing = () => {
        setFacing((prev) => (prev === 'back' ? 'front' : 'back'));
    };

    if (!permission) return null;

    if (!permission.granted) {
        return (
            <View style={styles.permissionContainer}>
                <Text style={styles.permissionText}>
                    We need your permission to show the camera
                </Text>
                <TouchableOpacity style={styles.button} onPress={requestPermission}>
                    <Text style={styles.text}>Grant Permission</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.container}>


            <ZegoUIKitPrebuiltCall
                ref={prebuiltRef}
                appID={appID}
                appSign={appSign}
                userID={userID}
                userName={userName}
                callID={callID}
                config={{
                    ...ONE_ON_ONE_VIDEO_CALL_CONFIG,
                    turnOnCameraWhenJoining: true,
                    turnOnMicrophoneWhenJoining: true,
                    useFrontCamera: true,
                    showAudioVideoToggleButton: true,
                    showAudioMuteButton: true,
                    showVideoMuteButton: true,
                    startCallInvitaiton: true,
                    avatarBuilder: ({ userInfo }) => (
                        <View style={{ width: '100%', height: '100%' }}>
                            <Image
                                source={pfp}
                                style={{ width: '100%', height: '100%' }}
                                resizeMode="cover"
                            />
                        </View>
                    ),
                    onCallEnd: () => navigation.navigate('/mentee-matching'),
                    timingConfig: {
                        isDurationVisible: true,
                        onDurationUpdate: (duration) => {
                            if (duration === 25 * 60) {
                                ZegoUIKitPrebuiltCallService.hangUp();
                            }
                        },
                    },
                    topMenuBarConfig: {
                        buttons: [ZegoMenuBarButtonName.minimizingButton],
                    },
                    onWindowMinimized: () => navigation.navigate('HomePage'),
                    onWindowMaximized: () =>
                        navigation.navigate('VoiceCallPage', {
                            userID,
                            userName,
                            callID,
                        }),
                }}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    camera: {
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: 300,
        zIndex: 10,
    },
    flipButton: {
        position: 'absolute',
        top: 320,
        alignSelf: 'center',
        zIndex: 10,
        padding: 10,
        backgroundColor: '#000',
        borderRadius: 8,
    },
    text: {
        color: '#fff',
        fontWeight: 'bold',
    },
    permissionContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    permissionText: {
        marginBottom: 10,
    },
    button: {
        padding: 12,
        backgroundColor: '#007AFF',
        borderRadius: 8,
    },
});
