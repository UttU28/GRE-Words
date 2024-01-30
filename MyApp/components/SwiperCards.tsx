import React, { useRef, useState } from 'react';
import { Text, View, StyleSheet, Button } from 'react-native';
import VideoPlayer from 'react-native-video-player';


const profile = {
    id: 1,
    videoURL: 'https://www.playphrase.me/video/5b96b007cc77853d88561aa4/628ea5c3b071e7f3ed0c0162.mp4',
    name: 'John Doe', // Set the name here
};

const SwiperCards = () => {
    const video = useRef(null);
    const [status, setStatus] = useState({});

    return (
        <View style={styles.card}>
            <Text style={styles.name}>{profile.name}</Text>
            {/* <VideoPlayer video={{uri: profile.videoURL}} autoplay={false}></VideoPlayer> */}
        </View>
    );
};

const styles = StyleSheet.create({
    name: {
        textAlign: 'center', // Add this to center the text
        fontSize: 18, // Set your desired font size
    },
    card: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center', // Center the content horizontally
        backgroundColor: '#ecf0f1',
    },
});

export default SwiperCards;
